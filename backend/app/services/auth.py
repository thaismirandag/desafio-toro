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
        print(f"Criando nova sessão para usuário {name} com ID {session_id}")

        self.table.put_item(Item={
            "session_id": session_id,
            "name": name
        })
        print("Sessão criada com sucesso")

        return session_id

    async def get_user_by_session(self, session_id: str) -> dict | None:
        print(f"Buscando usuário para sessão {session_id}")
        response = self.table.get_item(Key={"session_id": session_id})
        print(f"Resposta do DynamoDB: {response}")
        
        item = response.get("Item")
        print(f"Item encontrado: {item}")

        if not item:
            print("Nenhum item encontrado para esta sessão")
            return None

        print(f"Usuário encontrado: {item['name']}")
        return item  
