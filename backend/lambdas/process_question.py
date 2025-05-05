import json
import os
import boto3
from openai import OpenAI
from botocore.exceptions import ClientError
from datetime import datetime

def lambda_process_question(event, context):
    """
    Função Lambda para processar questões usando a OpenAI.
    Esta função é acionada pelo tópico SNS de processamento.
    """
    print("Iniciando processamento da questão...")
    print(f"Evento recebido: {json.dumps(event)}")
    
    question_id = None
    
    try:
        sns_message = event['Records'][0]['Sns']['Message']
        print(f"Mensagem SNS bruta: {sns_message}")
        
        message = json.loads(sns_message)
        print(f"Mensagem decodificada: {json.dumps(message, indent=2)}")
        
        if not isinstance(message, dict):
            raise ValueError(f"Mensagem inválida: não é um dicionário. Tipo recebido: {type(message)}")
        
        question_id = message.get('question_id')
        question_text = message.get('question')
        
        print(f"Campos encontrados na mensagem: {list(message.keys())}")
        print(f"question_id encontrado: {question_id}")
        print(f"question_text encontrado: {question_text}")
        
        if not question_id:
            raise ValueError(f"ID da questão não encontrado na mensagem. Campos disponíveis: {list(message.keys())}")
        
        if not question_text:
            raise ValueError(f"Texto da questão não encontrado na mensagem. Campos disponíveis: {list(message.keys())}")
        
        print(f"Processando questão ID: {question_id}")
        print(f"Pergunta: {question_text}")
        
        client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        
        print("Gerando resposta com OpenAI...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil e preciso."},
                {"role": "user", "content": question_text}
            ]
        )
        
        answer = response.choices[0].message.content
        print(f"Resposta gerada: {answer}")
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
        
        print(f"Atualizando questão no DynamoDB: {question_id}")
        table.update_item(
            Key={'id': question_id},
            UpdateExpression='SET answer = :answer, #st = :status, updated_at = :updated_at',
            ExpressionAttributeNames={
                '#st': 'status'  # Usando alias para evitar palavra reservada
            },
            ExpressionAttributeValues={
                ':answer': answer,
                ':status': 'respondida',
                ':updated_at': datetime.utcnow().isoformat()
            }
        )
        print("Status atualizado no DynamoDB para 'respondida'")
        
        response = table.get_item(Key={'id': question_id})
        current_status = response['Item']['status']
        print(f"Status atual da questão: {current_status}")
        
        if current_status != 'respondida':
            raise Exception(f"Erro ao atualizar status. Status atual: {current_status}")
        
        sns = boto3.client('sns')
        sns.publish(
            TopicArn=os.environ['SNS_TOPIC_NOTIFY'],
            Message=json.dumps({
                'question_id': question_id,
                'answer': answer,
                'status': 'respondida'
            })
        )
        print("Notificação publicada no SNS")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Questão processada com sucesso',
                'question_id': question_id,
                'status': current_status
            })
        }
        
    except Exception as e:
        print(f"Erro ao processar questão: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        print(f"Detalhes do erro: {str(e)}")
        
        if question_id:
            try:
                dynamodb = boto3.resource('dynamodb')
                table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
                
                table.update_item(
                    Key={'id': question_id},
                    UpdateExpression='SET #st = :status, error = :error, updated_at = :updated_at',
                    ExpressionAttributeNames={
                        '#st': 'status'
                    },
                    ExpressionAttributeValues={
                        ':status': 'erro',
                        ':error': str(e),
                        ':updated_at': datetime.utcnow().isoformat()
                    }
                )
                print("Status de erro atualizado no DynamoDB")
            except Exception as db_error:
                print(f"Erro ao atualizar status no DynamoDB: {str(db_error)}")
                print(f"Tipo do erro do DynamoDB: {type(db_error)}")
        else:
            print("Não foi possível atualizar o status no DynamoDB: question_id não disponível")
        
        raise e 