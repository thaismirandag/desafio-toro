from datetime import datetime

import boto3

from app.core.config import settings
from app.models.question import QuestionResponse


class DynamoDBService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        self.table = self.dynamodb.Table(settings.DYNAMODB_TABLE_QUESTIONS)

    def create_question(self, question: str, session_id: str) -> QuestionResponse:
        question_id = datetime.utcnow().isoformat()
        item = {
            'session_id': session_id,
            'id': question_id,
            'question': question,
            'status': 'pendente',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        self.table.put_item(Item=item)
        return QuestionResponse(**item)

    def get_question(self, question_id: str) -> QuestionResponse | None:
        response = self.table.get_item(Key={'id': question_id})
        item = response.get('Item')
        return QuestionResponse(**item) if item else None

    def update_question_with_answer(
        self,
        question_id: str,
        answer: str
    ) -> QuestionResponse:
        now = datetime.utcnow().isoformat()
        
        self.table.update_item(
            Key={'id': question_id},
            UpdateExpression=(
                'SET answer = :a, '
                'status = :s, '
                'updated_at = :t'
            ),
            ExpressionAttributeValues={
                ':a': answer,
                ':s': 'respondida',
                ':t': now
            },
            ReturnValues='ALL_NEW'
        )
        
        return self.get_question(question_id) 