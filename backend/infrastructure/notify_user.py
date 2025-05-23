import json
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

def handler(event, context):
    """
    Lambda que notifica o usuário quando uma resposta está pronta.
    - Recebe a notificação do SNS
    - Recupera a pergunta e resposta do DynamoDB
    - Envia a notificação (neste caso, apenas log)
    """
    try:
        message = json.loads(event['Records'][0]['Sns']['Message'])
        question_id = message.get('question_id')

        if not question_id:
            raise ValueError("question_id ausente na mensagem SNS.")


        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(settings.DYNAMODB_TABLE_QUESTIONS)
        
        response = table.get_item(Key={'id': question_id})
        if 'Item' not in response:
            raise ValueError(f"Nenhuma questão encontrada com ID: {question_id}")
        
        item = response['Item']
        current_status = item.get('status', 'desconhecido')

        if current_status != 'respondida':
            print(f"Corrigindo status para 'respondida' (atual: {current_status})...")
            table.update_item(
                Key={'id': question_id},
                UpdateExpression='SET #st = :status',
                ExpressionAttributeNames={'#st': 'status'},
                ExpressionAttributeValues={':status': 'respondida'}
            )


        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Notificação enviada com sucesso',
                'question_id': question_id
            })
        }

    except ClientError as e:
        print(f"Erro ao acessar o DynamoDB: {e.response['Error']['Message']}")
        raise
    except Exception:
        raise
