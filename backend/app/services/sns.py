import json

import boto3

from app.core.config import settings


class SNSService:
    def __init__(self):
        self.sns = boto3.client('sns',
            region_name=settings.AWS_REGION
        )
        
    def publish_to_process(self, question_id: str, question: str):
        try:
            message = {
                'question_id': question_id,
                'question': question
            }
            
            topic_arn = settings.sns_topic_process
            
            response = self.sns.publish(
                TopicArn=topic_arn,
                Message=json.dumps(message)
            )

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
            
            response = self.sns.publish(
                TopicArn=topic_arn,
                Message=json.dumps(message)
            )

            return response
        except Exception as e:
            print(f"Erro ao publicar no SNS: {str(e)}")
            print(f"Tipo do erro: {type(e)}")
            raise

sns_service = SNSService()