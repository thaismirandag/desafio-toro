import uuid
from datetime import datetime, timedelta
from typing import Optional
import boto3
import os

dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION"))
SESSIONS_TABLE_NAME = os.getenv("SESSIONS_TABLE", "sessions")
table = dynamodb.Table(SESSIONS_TABLE_NAME)

class AuthService:
    async def login(self, name: str) -> Optional[str]:
        session_id = str(uuid.uuid4())
        expires_at = (datetime.utcnow() + timedelta(hours=24)).isoformat()

        table.put_item(Item={
            "session_id": session_id,
            "name": name,
            "expires_at": expires_at
        })

        return session_id

    async def get_user_by_session(self, session_id: str) -> Optional[str]:
        response = table.get_item(Key={"session_id": session_id})
        item = response.get("Item")

        if not item:
            return None

        expires_at = datetime.fromisoformat(item["expires_at"])
        if expires_at < datetime.utcnow():
            table.delete_item(Key={"session_id": session_id})
            return None

        return item["name"]
