import uuid

import boto3

from app.core.config import settings


class AuthService:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=settings.AWS_REGION
        )
        self.table = self.dynamodb.Table(settings.DYNAMODB_TABLE_SESSIONS)


    async def login(self, name: str) -> str | None:
        session_id = str(uuid.uuid4())

        self.table.put_item(Item={
            "session_id": session_id,
            "name": name
        })

        return session_id

    async def get_user_by_session(self, session_id: str) -> dict | None:
        response = self.table.get_item(Key={"session_id": session_id})
        
        item = response.get("Item")

        if not item:
            return None
        
        return item  
