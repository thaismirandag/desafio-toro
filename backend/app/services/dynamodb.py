import boto3
from datetime import datetime
from typing import Optional
from app.core.config import settings
from app.models.question import QuestionInDB, QuestionStatus

class DynamoDBService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        self.table = self.dynamodb.Table(settings.DYNAMODB_TABLE)

    def create_question(self, question: str) -> QuestionInDB:
        question_id = datetime.utcnow().isoformat()
        item = {
            'id': question_id,
            'question': question,
            'status': QuestionStatus.PENDING,
            'created_at': datetime.utcnow().isoformat(),
        }
        
        self.table.put_item(Item=item)
        return QuestionInDB(**item)

    def get_question(self, question_id: str) -> Optional[QuestionInDB]:
        response = self.table.get_item(Key={'id': question_id})
        item = response.get('Item')
        return QuestionInDB(**item) if item else None

    def update_question_with_answer(self, question_id: str, answer: str) -> QuestionInDB:
        now = datetime.utcnow().isoformat()
        item = {
            'id': question_id,
            'answer': answer,
            'status': QuestionStatus.ANSWERED,
            'answered_at': now
        }
        
        self.table.update_item(
            Key={'id': question_id},
            UpdateExpression='SET answer = :a, status = :s, answered_at = :t',
            ExpressionAttributeValues={
                ':a': answer,
                ':s': QuestionStatus.ANSWERED,
                ':t': now
            },
            ReturnValues='ALL_NEW'
        )
        
        return self.get_question(question_id) 