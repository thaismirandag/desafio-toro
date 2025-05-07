import json
import boto3
import openai
from botocore.exceptions import ClientError
from app.core.config import settings

dynamodb = boto3.resource('dynamodb')
sns_client = boto3.client('sns')

openai.api_key = settings.OPENAI_API_KEY

def lambda_process_question(event, context):
    """
    Lambda que processa uma pergunta:
    - Recebe mensagem do SQS
    - Busca pergunta no DynamoDB
    - Gera resposta via OpenAI
    - Atualiza item com a resposta
    - Publica notificação no SNS
    """
    try:
        print("Evento recebido:")
        print(json.dumps(event))

        message = json.loads(event['Records'][0]['body'])
        question_id = message.get('question_id')

        if not question_id:
            raise ValueError("Campo 'question_id' ausente na mensagem.")

        table = dynamodb.Table(settings.DYNAMODB_TABLE_QUESTIONS)
        response = table.get_item(Key={'id': question_id})

        if 'Item' not in response:
            raise ValueError(
                f"Item com ID {question_id} não encontrado no DynamoDB."
            )

        item = response['Item']
        question_text = item.get('question', '').strip()

        if not question_text:
            raise ValueError(
                f"Item com ID {question_id} não contém uma pergunta válida."
            )

        print(f"Pergunta: {question_text}")

        ai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente prestativo e amigável."
                },
                {"role": "user", "content": question_text}
            ]
        )

        answer = ai_response.choices[0].message['content'].strip()
        print(f"Resposta gerada: {answer}")

        table.update_item(
            Key={'id': question_id},
            UpdateExpression="SET answer = :a, #st = :s",
            ExpressionAttributeNames={"#st": "status"},
            ExpressionAttributeValues={
                ":a": answer,
                ":s": "respondida"
            }
        )

        sns_topic_arn = settings.sns_topic_notify
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=json.dumps({'question_id': question_id})
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Pergunta processada com sucesso',
                'question_id': question_id
            })
        }

    except ClientError as e:
        print(f"Erro na AWS: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        print(f"Erro geral: {e!s}")
        raise
