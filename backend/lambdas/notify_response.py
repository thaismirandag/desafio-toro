import json
import boto3
import os
from datetime import datetime

def lambda_notify_response(event, context):
    """
    Função Lambda para notificar quando uma resposta estiver pronta.
    Esta função é acionada pelo tópico SNS de notificação.
    """
    print("Iniciando processamento de notificação...")
    print(f"Evento recebido: {json.dumps(event)}")
    
    try:
        message = json.loads(event['Records'][0]['Sns']['Message'])
        print(f"Mensagem recebida: {json.dumps(message)}")
        
        question_id = message.get('question_id')
        if not question_id:
            raise ValueError("ID da questão não encontrado na mensagem")
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
        
        response = table.get_item(Key={'id': question_id})
        item = response.get('Item')
        
        if item:
            print(f"Detalhes da questão: {json.dumps(item)}")
        else:
            print(f"Questão não encontrada: {question_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Notificação processada com sucesso',
                'question_id': question_id
            })
        }
        
    except Exception as e:
        print(f"Erro ao processar notificação: {str(e)}")
        raise e 