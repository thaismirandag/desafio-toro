import json
import uuid
from datetime import datetime

import boto3
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
        print("QuestionService inicializado com sucesso")
    
    async def create_question(self, question: str, session_id: str) -> QuestionResponse:
        try:
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
                        
            try:
                self.table.put_item(Item=question_data)
                print(f"Questão salva no DynamoDB: {question_id}")
            except ClientError as e:
                print(f"Erro ao salvar no DynamoDB: {e!s}")
                raise Exception("Erro ao salvar questão no DynamoDB") from e
            
            try:
                self.sns.publish_to_process(question_id, question)
            except Exception as e:
                print(f"Erro ao publicar no SNS: {e!s}")
                raise Exception("Erro ao publicar mensagem no SNS") from e
            
            return QuestionResponse(**question_data)
        except Exception as e:
            print(f"Erro ao criar questão: {e!s}")
            raise Exception("Erro ao criar questão") from e
    
    async def list_questions(self, session_id: str, limit: int = 10) -> list[QuestionResponse]:
        try:
            
            response = self.table.query(
                IndexName='SessionIndex', 
                KeyConditionExpression='session_id = :session_id',
                ExpressionAttributeValues={
                    ':session_id': session_id
                },
                ScanIndexForward=False,  
                Limit=limit
            )
            
            items = response.get('Items', [])
            
            items.sort(key=lambda x: x['created_at'], reverse=True)
            
            return [QuestionResponse(**item) for item in items]
            
        except ClientError as e:
            print(f"Erro ao consultar DynamoDB: {e!s}")
            raise Exception("Erro ao listar perguntas no DynamoDB") from e
