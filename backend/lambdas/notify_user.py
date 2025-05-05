import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')

def lambda_notify_user(event, context):
    """
    Lambda que notifica o usuário quando uma resposta está pronta.
    - Recebe a notificação do SNS
    - Recupera a pergunta e resposta do DynamoDB
    - Envia a notificação (neste caso, apenas o log)
    """
    try:
        message = json.loads(event['Records'][0]['Sns']['Message'])
        question_id = message['question_id']
        
        table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
        response = table.get_item(Key={'id': question_id})  
        item = response['Item']
        
        # Garante que o status permaneça como 'respondida'
        if item['status'] != 'respondida':
            table.update_item(
                Key={'id': question_id},
                UpdateExpression='SET #st = :status',
                ExpressionAttributeNames={
                    '#st': 'status'
                },
                ExpressionAttributeValues={
                    ':status': 'respondida'
                }
            )
            print(f"Status corrigido para 'respondida'")
        
        print(f"""
        Nova resposta disponível!
        Pergunta: {item['question']}
        Resposta: {item['answer']}
        ID: {question_id}
        Status: {item['status']}
        """)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Notificação enviada com sucesso',
                'question_id': question_id
            })
        }
        
    except Exception as e:
        print(f"Erro ao enviar notificação: {str(e)}")
        raise 