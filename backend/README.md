# Backend do Desafio Toro

Este é o backend do Desafio Toro, construído com FastAPI e integrado com serviços AWS.

## Estrutura do Projeto

```
backend/
    app/
        models/
            question.py  # Modelos relacionados a perguntas
            user.py      # Modelos relacionados a usuários
        services/
            auth.py      # Serviço de autenticação
            question.py  # Serviço de perguntas
        api/
            v1/
                auth.py    # Rotas de autenticação
                router.py  # Rotas de perguntas
    lambdas/
        notify_user.py  # Lambda de notificação
        process_question.py  # Lambda de processamento de pergunta
    infrastructure/
        app.py  # configuração do cdk
        cdk.json
    tests/

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

4. Inicie o servidor:
```bash
poetry run start
```

### Docker

Para executar com Docker:

```bash
docker-compose up -d
``` 

A API estará disponível em http://localhost:8000
A documentação da API estará em http://localhost:8000/docs 