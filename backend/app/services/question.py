import json
import uuid
from datetime import datetime

import boto3
import openai
from botocore.exceptions import ClientError

from app.core.config import settings
from app.models.question import QuestionResponse
from app.services.sns import SNSService


class QuestionService:
    def __init__(self):
        print("Inicializando QuestionService...")
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=settings.AWS_REGION
        )
        print(f"Região AWS: {settings.AWS_REGION}")
        self.table = self.dynamodb.Table(settings.DYNAMODB_TABLE_QUESTIONS)
        print(f"Tabela DynamoDB: {settings.DYNAMODB_TABLE_QUESTIONS}")
        self.sns = SNSService()
        openai.api_key = settings.OPENAI_API_KEY
        print("QuestionService inicializado com sucesso")
    
    async def create_question(self, question: str, session_id: str) -> QuestionResponse:
        try:
            print(f"Iniciando criação de questão para sessão {session_id}")
            question_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            
            question_data = {
                'id': question_id,
                'answer': None,
                'question': question,
                'session_id': session_id,
                'status': 'pendente',
                'created_at': now,
                'updated_at': now
            }
            
            print(f"Criando questão: {json.dumps(question_data, default=str)}")
            
            try:
                print("Salvando questão no DynamoDB...")
                self.table.put_item(Item=question_data)
                print(f"Questão salva no DynamoDB: {question_id}")
            except ClientError as e:
                print(f"Erro ao salvar no DynamoDB: {e!s}")
                print(f"Detalhes do erro: {e.response['Error'] if hasattr(e, 'response') else 'Sem detalhes'}")
                raise Exception("Erro ao salvar questão no DynamoDB") from e
            
            try:
                print("Iniciando publicação no SNS...")
                self.sns.publish_to_process(question_id, question)
                print("Mensagem publicada no SNS com sucesso")
            except Exception as e:
                print(f"Erro ao publicar no SNS: {e!s}")
                print(f"Tipo do erro: {type(e)}")
                raise Exception("Erro ao publicar mensagem no SNS") from e
            
            return QuestionResponse(**question_data)
        except Exception as e:
            print(f"Erro ao criar questão: {e!s}")
            print(f"Tipo do erro: {type(e)}")
            raise Exception("Erro ao criar questão") from e
    
    async def list_questions(self, session_id: str) -> list[QuestionResponse]:
        try:
            print(f"Listando questões para usuário: {session_id}")
            
            response = self.table.scan(
                FilterExpression='session_id = :session_id',
                ExpressionAttributeValues={':session_id': session_id}
            )
            items = response.get('Items', [])
            print(f"Encontradas {len(items)} questões")
            for item in items:
                print(f"Questão ID: {item['id']}, Status: {item['status']}")
            return [QuestionResponse(**item) for item in items]
        except ClientError as e:
            print(f"Erro detalhado: {e!s}")
            raise Exception("Erro ao listar perguntas no DynamoDB") from e
    
    async def answer_question(self, question_id: str, answer: str) -> QuestionResponse:
        try:
            print(f"Buscando questão: {question_id}")
            
            response = self.table.get_item(Key={'id': question_id})
            item = response.get('Item')
            if not item:
                raise Exception("Pergunta não encontrada")
            
            try:
                print(f"Gerando resposta para pergunta: {item['question']}")
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "Você é um assistente prestativo e preciso."
                        },
                        {"role": "user", "content": item['question']}
                    ]
                )
                ai_answer = completion.choices[0].message['content']
                print(f"Resposta gerada: {ai_answer}")
            except Exception as e:
                print(f"Erro ao gerar resposta com OpenAI: {e!s}")
                raise Exception("Erro ao gerar resposta com OpenAI") from e
            
            item['answer'] = ai_answer
            item['status'] = 'respondida'
            item['updated_at'] = datetime.utcnow().isoformat()
            
            print(f"Atualizando questão no DynamoDB: {question_id}")
            self.table.put_item(Item=item)
            print("Questão atualizada com sucesso")
            
            return QuestionResponse(**item)
        except ClientError as e:
            print(f"Erro detalhado: {e!s}")
            raise Exception("Erro ao responder pergunta no DynamoDB") from e
