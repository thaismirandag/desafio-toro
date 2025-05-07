# Backend do Desafio Toro

Este é o backend do Desafio Toro, construído com FastAPI e integrado com serviços AWS. O sistema processa perguntas de forma assíncrona usando AWS Lambda, SNS e DynamoDB.

## Arquitetura

O sistema utiliza uma arquitetura assíncrona com os seguintes componentes:

1. **API Gateway + FastAPI**: Recebe as requisições HTTP
2. **DynamoDB**: Armazena perguntas e sessões de usuário
3. **SNS**: Gerencia o fluxo de mensagens entre os componentes
4. **Lambda Functions**: Processam as perguntas e enviam notificações

### Fluxo de Processamento

1. Usuário envia uma pergunta via API
2. A pergunta é salva no DynamoDB com status "pendente"
3. Um tópico SNS é acionado para processar a pergunta
4. Lambda processa a pergunta usando OpenAI
5. A resposta é salva no DynamoDB e status é atualizado para "respondida"
6. Um segundo tópico SNS notifica sobre a resposta disponível

## Clean Code e Escalabilidade

### Princípios de Clean Code

1. **Separação de Responsabilidades**
   - Serviços isolados para cada domínio (QuestionService, SNSService)
   - Rotas da API separadas por funcionalidade
   - Configurações centralizadas em módulos específicos



### Escalabilidade

1. **Arquitetura Serverless**
   - Escalamento automático com Lambda
   - Sem necessidade de gerenciar servidores



## Estrutura do Projeto

```
backend/
    app/
        core/
            config.py      # Configurações da aplicação
        models/
            question.py    # Modelos relacionados a perguntas
            user.py        # Modelos relacionados a usuários
        services/
            auth.py        # Serviço de autenticação
            question.py    # Serviço de perguntas
            dynamodb.py    # Serviço de acesso ao DynamoDB
            sns.py         # Serviço de mensageria SNS
        api/
            v1/
                auth.py    # Rotas de autenticação
                questions.py # Rotas de perguntas
    infrastructure/
        app.py            # Configuração do CDK
        process_question.py # Lambda de processamento
        notify_user.py    # Lambda de notificação
        lambda_handler.py # Handler principal do FastAPI
        requirements.txt  # Dependências do Lambda
        cdk.json         # Configuração do CDK
        README.md        # Documentação da infraestrutura
    tests/ # Testes ainda não implementados
```

## Desenvolvimento

### Pré-requisitos
- Python 3.11
- Poetry
- Docker e Docker Compose 
- AWS CLI
- CDK

### Instalação

1. Instale as dependências:
```bash
poetry install
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```

3. Execute os testes:
```bash
poetry run pytest
```

4. Inicie o servidor local:
```bash
poetry run start
```

### Infraestrutura AWS

1. Configure suas credenciais AWS:
```bash
aws configure
```

2. Faça o deploy da infraestrutura:
```bash
cd infrastructure
./build_lambda.sh  # Constrói o pacote Lambda
cdk deploy        # Deploy da infraestrutura
```

### Docker

Para executar localmente com Docker:

```bash
docker-compose up -d
``` 

A API estará disponível em http://localhost:8000
A documentação da API estará em http://localhost:8000/docs

## Endpoints

### Autenticação
- `POST /api/v1/auth/login`: Login de usuário

### Perguntas
- `POST /api/v1/questions`: Envia uma nova pergunta
- `GET /api/v1/questions/{session_id}`: Consulta as perguntas do usuário

## Melhorias Futuras

### Performance e Escalabilidade
1. **Cache Distribuído**
   - Implementação de Redis para cache de respostas frequentes
   - Redução de latência para perguntas similares
   - Otimização de custos com DynamoDB

2. **Processamento em Lote**
   - Implementação de filas SQS para processamento em lote
   - Otimização de recursos Lambda

### Monitoramento e Observabilidade
1. **Monitoramento de Serviços**
   - Dashboards personalizados no CloudWatch
   - Visualização de logs e métricas com Kibana
   - Alertas automáticos para anomalias
   - Monitoramento de saúde dos serviços AWS
   - Análise de tendências e padrões de uso

### Segurança
1. **Autenticação e Autorização**
   - Implementação de JWT com refresh tokens
   - Integração com AWS Cognito


### Testes e Qualidade
1. **Cobertura de Testes**
   - Implementação de testes unitários
   - Testes de integração com serviços AWS

2. **CI/CD**
   - Pipeline automatizado com GitHub Actions
   - Validação automática de infraestrutura






