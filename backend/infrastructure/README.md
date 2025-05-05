# Infraestrutura do Desafio Toro

Este diretório contém a infraestrutura como código (IaC) do projeto usando AWS CDK.

## Pré-requisitos

1. Python 3.9 ou superior
2. AWS CLI configurado com credenciais válidas
3. Node.js 14 ou superior (necessário para o CDK)

## Configuração do Ambiente

1. Crie um ambiente virtual Python:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Instale o AWS CDK globalmente:
```bash
npm install -g aws-cdk
```

## Deploy da Infraestrutura

1. Bootstrap do CDK (apenas na primeira vez):
```bash
cdk bootstrap
```

2. Sintetize o CloudFormation template:
```bash
cdk synth
```

3. Faça o deploy da stack:
```bash
cdk deploy
```

## Estrutura da Infraestrutura

A infraestrutura inclui:
- DynamoDB Table para armazenar perguntas e respostas
- SNS Topics para processamento e notificação
- Lambda Functions para processamento e notificação
- API Gateway para expor endpoints REST
- IAM Roles e Policies necessárias

## Limpeza

Para remover todos os recursos criados:
```bash
cdk destroy
``` 