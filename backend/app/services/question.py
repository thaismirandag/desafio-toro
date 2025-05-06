from datetime import datetime
import uuid
from typing import List
import boto3
from botocore.exceptions import ClientError
from openai import OpenAI
from app.models.question import QuestionResponse
from app.core.config import settings
from app.services.sns import SNSService
import json


class QuestionService:
    def __init__(self):
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.dynamodb = session.resource('dynamodb')
        self.table = self.dynamodb.Table(settings.DYNAMODB_TABLE)
        self.sns = SNSService()
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def create_question(self, question: str, user_name: str) -> dict:
        question_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        question_data = {
            'id': question_id,
            'answer': None,
            'question': question,
            'user_id': user_name,  
            'status': 'pendente',
            'created_at': now,
            'updated_at': now
        }
        
        print(f"Criando questão: {json.dumps(question_data, default=str)}")
        
        self.table.put_item(Item=question_data)
        print(f"Questão salva no DynamoDB: {question_id}")
        
        self.sns.publish_to_process(question_id, question)
        
        return question_data
    
    
    async def list_questions(self, user_name: str) -> List[QuestionResponse]:
        try:
            print(f"Listando questões para usuário: {user_name}")
            
            response = self.table.scan(
                FilterExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_name}
            )
            items = response.get('Items', [])
            print(f"Encontradas {len(items)} questões")
            for item in items:
                print(f"Questão ID: {item['id']}, Status: {item['status']}")
            return [QuestionResponse(**item) for item in items]
        except ClientError as e:
            print(f"Erro detalhado: {str(e)}")
            raise Exception(f"Erro ao listar perguntas no DynamoDB: {str(e)}")
    
    async def answer_question(self, question_id: str, answer: str) -> QuestionResponse:
        try:
            print(f"Buscando questão: {question_id}")
            
            response = self.table.get_item(Key={'id': question_id})
            item = response.get('Item')
            if not item:
                raise Exception("Pergunta não encontrada")
            
            try:
                print(f"Gerando resposta para pergunta: {item['question']}")
                completion = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Você é um assistente prestativo e preciso."},
                        {"role": "user", "content": item['question']}
                    ]
                )
                ai_answer = completion.choices[0].message.content
                print(f"Resposta gerada: {ai_answer}")
            except Exception as e:
                print(f"Erro ao gerar resposta com OpenAI: {str(e)}")
                raise Exception("Erro ao gerar resposta com OpenAI")
            
            item['answer'] = ai_answer
            item['status'] = 'respondida'
            item['updated_at'] = datetime.utcnow().isoformat()
            
            print(f"Atualizando questão no DynamoDB: {question_id}")
            self.table.put_item(Item=item)
            print("Questão atualizada com sucesso")
            
            return QuestionResponse(**item)
        except ClientError as e:
            print(f"Erro detalhado: {str(e)}")
            raise Exception(f"Erro ao responder pergunta no DynamoDB: {str(e)}")
