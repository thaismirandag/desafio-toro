# Backend do Desafio Toro

Este é o backend do Desafio Toro, construído com FastAPI e integrado com serviços AWS.

## Estrutura do Projeto

```
backend/
├── app/
│   ├── api/        # Endpoints da API
│   ├── core/       # Configurações e utilitários
│   ├── models/     # Modelos de dados
│   ├── schemas/    # Schemas Pydantic
│   └── services/   # Serviços e lógica de negócio
└── tests/          # Testes automatizados
```

## Desenvolvimento

### Pré-requisitos
- Python 3.11
- Poetry
- Docker e Docker Compose (opcional)

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