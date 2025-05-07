# Desafio Toro

Projeto fullstack com backend em FastAPI e frontend em javascript.

## Estrutura do Projeto

```
.
├── architecture.png # Diagrama de arquitetura
├── backend/           # API FastAPI
│   ├── app/          # Código fonte
│   └── tests/        # Testes
│   └── infrastructure/ # Infraestrutura
│   └── lambda_package/ # Pacote para Lambda
└── frontend/         # frontend ainda não implementado

```

## Backend

### Pré-requisitos
- Docker
- Docker Compose
- Python 3.11
- Poetry

### Instalação

1. Instale as dependências:
```bash
cd backend
poetry install
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações

```

3. Inicie o servidor:
```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Frontend


## Desenvolvimento

### Backend

- Lint: `poetry run ruff check .`
- Formatação: `poetry run black .`
- Testes: `poetry run pytest`



