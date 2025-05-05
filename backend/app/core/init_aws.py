import boto3
import os
from botocore.exceptions import ClientError
from app.core.config import settings
import json
import zipfile
import shutil

def create_dynamodb_table():
    dynamodb = boto3.resource('dynamodb',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    
    try:
        table = dynamodb.create_table(
            TableName=settings.DYNAMODB_TABLE,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH' 
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"Tabela {settings.DYNAMODB_TABLE} criada com sucesso!")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Tabela {settings.DYNAMODB_TABLE} já existe.")
        else:
            raise e

def create_sns_topics():
    sns = boto3.client('sns',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    
    try:
        response = sns.create_topic(Name=settings.SNS_TOPIC_PROCESS)
        settings.SNS_TOPIC_PROCESS = response['TopicArn']
        print(f"Tópico SNS de processamento criado: {settings.SNS_TOPIC_PROCESS}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidParameter':
            response = sns.get_topic_attributes(TopicArn=settings.SNS_TOPIC_PROCESS)
            print(f"Tópico SNS de processamento já existe: {settings.SNS_TOPIC_PROCESS}")
        else:
            raise e
    
    try:
        response = sns.create_topic(Name=settings.SNS_TOPIC_NOTIFY)
        settings.SNS_TOPIC_NOTIFY = response['TopicArn']
        print(f"Tópico SNS de notificação criado: {settings.SNS_TOPIC_NOTIFY}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidParameter':
            response = sns.get_topic_attributes(TopicArn=settings.SNS_TOPIC_NOTIFY)
            print(f"Tópico SNS de notificação já existe: {settings.SNS_TOPIC_NOTIFY}")
        else:
            raise e

def create_lambda_function():
    lambda_client = boto3.client('lambda',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    
    sns_client = boto3.client('sns',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    
    function_name = 'process-question'
    
    try:
        lambda_client.get_function(FunctionName=function_name)
        print(f"Função Lambda {function_name} já existe.")
        
        function_arn = lambda_client.get_function(FunctionName=function_name)['Configuration']['FunctionArn']
        print(f"ARN da função Lambda: {function_arn}")
        
        subscriptions = sns_client.list_subscriptions_by_topic(TopicArn=settings.SNS_TOPIC_PROCESS)
        lambda_subscribed = False
        
        for subscription in subscriptions.get('Subscriptions', []):
            if subscription['Protocol'] == 'lambda' and subscription['Endpoint'] == function_arn:
                lambda_subscribed = True
                print(f"Lambda já está inscrita no tópico: {subscription['SubscriptionArn']}")
                break
        
        if not lambda_subscribed:
            response = sns_client.subscribe(
                TopicArn=settings.SNS_TOPIC_PROCESS,
                Protocol='lambda',
                Endpoint=function_arn
            )
            print(f"Nova inscrição criada: {response['SubscriptionArn']}")
            
            try:
                lambda_client.add_permission(
                    FunctionName=function_name,
                    StatementId='sns-invoke',
                    Action='lambda:InvokeFunction',
                    Principal='sns.amazonaws.com',
                    SourceArn=settings.SNS_TOPIC_PROCESS
                )
                print("Permissão SNS adicionada com sucesso!")
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceConflictException':
                    print("Permissão SNS já existe.")
                else:
                    raise e
        
        return
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceNotFoundException':
            raise e
    
    lambda_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'lambdas')
    zip_path = os.path.join(lambda_dir, 'process_question.zip')
    
    temp_dir = os.path.join(lambda_dir, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        lambda_code_path = os.path.join(lambda_dir, 'process_question.py')
        shutil.copy2(lambda_code_path, temp_dir)
        
        print("Criando ambiente virtual...")
        venv_path = os.path.join(temp_dir, 'venv')
        os.system(f'python -m venv {venv_path}')
        
        if os.name == 'nt':  # Windows
            pip_path = os.path.join(venv_path, 'Scripts', 'pip')
        else:  # Linux/Mac
            pip_path = os.path.join(venv_path, 'bin', 'pip')
        
        print("Instalando dependências...")
        os.system(f'{pip_path} install --upgrade pip')
        os.system(f'{pip_path} install --platform manylinux2014_x86_64 --target={temp_dir} --implementation cp --python-version 3.9 --only-binary=:all: --upgrade -r {os.path.join(lambda_dir, "requirements.txt")}')

        print("Criando arquivo ZIP...")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.pyc') or file.endswith('.pyo') or file.endswith('.dist-info') or file.endswith('.egg-info'):
                        continue
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        print("Arquivo ZIP criado com sucesso!")
        
        with open(zip_path, 'rb') as f:
            zip_bytes = f.read()
        
        try:
            sts_client = boto3.client('sts',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            account_id = sts_client.get_caller_identity()['Account']
            
            role_arn = 'arn:aws:iam::977099002762:role/role-lambdas'
            
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.9',
                Role=role_arn,
                Handler='process_question.lambda_process_question',
                Code={
                    'ZipFile': zip_bytes
                },
                Environment={
                    'Variables': {
                        'DYNAMODB_TABLE': settings.DYNAMODB_TABLE,
                        'SNS_TOPIC_NOTIFY': settings.SNS_TOPIC_NOTIFY,
                        'OPENAI_API_KEY': settings.OPENAI_API_KEY
                    }
                },
                Timeout=30,
                MemorySize=256
            )
            print(f"Função Lambda {function_name} criada com sucesso!")
            
            function_arn = response['FunctionArn']
            
            response = sns_client.subscribe(
                TopicArn=settings.SNS_TOPIC_PROCESS,
                Protocol='lambda',
                Endpoint=function_arn
            )
            print(f"Inscrição criada: {response['SubscriptionArn']}")
            
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId='sns-invoke',
                Action='lambda:InvokeFunction',
                Principal='sns.amazonaws.com',
                SourceArn=settings.SNS_TOPIC_PROCESS
            )
            print("Permissão SNS adicionada com sucesso!")
            
        except ClientError as e:
            print(f"Erro ao criar função Lambda: {str(e)}")
            raise e
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def init_aws_resources():
    create_dynamodb_table()
    create_sns_topics()
    create_lambda_function()
    print("Recursos AWS inicializados com sucesso!")