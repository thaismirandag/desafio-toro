# Desafio Toro

Projeto fullstack com backend em FastAPI e frontend em Angular.

## Estrutura do Projeto

```
.
├── backend/           # API FastAPI
│   ├── app/          # Código fonte
│   └── tests/        # Testes
└── frontend/         # Aplicação Angular
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

### Pré-requisitos

- Node.js 18+
- npm ou yarn

### Instalação

1. Instale as dependências:
```bash
cd frontend
npm install
```

2. Configure as variáveis de ambiente:
```bash
cp src/environments/environment.example.ts src/environments/environment.ts
# Edite o arquivo com suas configurações
```

3. Inicie o servidor de desenvolvimento:
```bash
ng serve
```

## Desenvolvimento

### Backend

- Lint: `poetry run ruff check .`
- Formatação: `poetry run black .`
- Testes: `poetry run pytest`

### Frontend

- Lint: `ng lint`
- Testes: `ng test`
- Build: `ng build`

