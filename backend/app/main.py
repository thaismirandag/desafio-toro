from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import SecurityScheme, SecuritySchemeType

from app.api.api import api_router
from app.core.config import settings
from app.core.init_aws import init_aws_resources

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configurar segurança do Swagger
app.openapi_components = {
    "securitySchemes": {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
}

# Configurar segurança global
app.openapi_security = [{"bearerAuth": []}]

app.openapi_tags = [
    {
        "name": "auth",
        "description": "Operações de autenticação",
    },
    {
        "name": "questions",
        "description": "Operações relacionadas a perguntas",
    }
]

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar recursos AWS
@app.on_event("startup")
async def startup_event():
    try:
        init_aws_resources()
    except Exception as e:
        print(f"Erro ao inicializar recursos AWS: {str(e)}")
        raise

# Incluir rotas
app.include_router(api_router, prefix=settings.API_V1_STR) 