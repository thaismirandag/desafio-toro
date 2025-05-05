import boto3
import json
from app.core.config import settings

class SNSService:
    def __init__(self):
        self.sns = boto3.client('sns',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    
    def publish_to_process(self, question_id: str, question: str):
        message = {
            'question_id': question_id,
            'question': question
        }
        
        print(f"Publicando mensagem no tópico de processamento: {json.dumps(message)}")
        response = self.sns.publish(
            TopicArn=settings.SNS_TOPIC_PROCESS,
            Message=json.dumps(message)
        )
        print(f"Mensagem publicada com sucesso! MessageId: {response['MessageId']}")
        return response
    
    def publish_to_notify(self, question_id: str, status: str):
        message = {
            'question_id': question_id,
            'status': status,
            'type': 'notification'
        }
        
        print(f"Publicando mensagem no tópico de notificação: {json.dumps(message)}")
        response = self.sns.publish(
            TopicArn=settings.SNS_TOPIC_NOTIFY,
            Message=json.dumps(message)
        )
        print(f"Mensagem publicada com sucesso! MessageId: {response['MessageId']}")
        return response

sns_service = SNSService()