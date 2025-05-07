import json

import boto3

from app.core.config import settings


class SNSService:
    def __init__(self):
        print("Inicializando SNSService...")
        print(f"Região AWS: {settings.AWS_REGION}")
        print(f"AWS Account ID: {settings.AWS_ACCOUNT_ID}")
        print(f"Tópico Process: {settings.SNS_TOPIC_PROCESS_NAME}")
        print(f"Tópico Notify: {settings.SNS_TOPIC_NOTIFY_NAME}")
        
        self.sns = boto3.client('sns',
            region_name=settings.AWS_REGION
        )
        print("SNSService inicializado com sucesso")
    
    def publish_to_process(self, question_id: str, question: str):
        try:
            message = {
                'question_id': question_id,
                'question': question
            }
            
            topic_arn = settings.sns_topic_process
            print(f"ARN do tópico de processamento: {topic_arn}")
            print(f"Publicando mensagem no tópico de processamento: {json.dumps(message)}")
            
            response = self.sns.publish(
                TopicArn=topic_arn,
                Message=json.dumps(message)
            )
            print(f"Mensagem publicada com sucesso! MessageId: {response['MessageId']}")
            return response
        except Exception as e:
            print(f"Erro ao publicar no SNS: {str(e)}")
            print(f"Tipo do erro: {type(e)}")
            raise
    
    def publish_to_notify(self, question_id: str, status: str):
        try:
            message = {
                'question_id': question_id,
                'status': status,
                'type': 'notification'
            }
            
            topic_arn = settings.sns_topic_notify
            print(f"ARN do tópico de notificação: {topic_arn}")
            print(f"Publicando mensagem no tópico de notificação: {json.dumps(message)}")
            
            response = self.sns.publish(
                TopicArn=topic_arn,
                Message=json.dumps(message)
            )
            print(f"Mensagem publicada com sucesso! MessageId: {response['MessageId']}")
            return response
        except Exception as e:
            print(f"Erro ao publicar no SNS: {str(e)}")
            print(f"Tipo do erro: {type(e)}")
            raise

sns_service = SNSService()