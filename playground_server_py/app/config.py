import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

APP_TITLE = "REST Server — Curso de Integrações"
APP_DESCRIPTION = (
    "Servidor REST modular para prática de integrações de sistemas. "
    "Autenticação via API Key (header X-API-Key) com controle de acesso por roles."
)
APP_VERSION = "0.1.0"

ADMIN_NAME = "Admin"
ADMIN_EMAIL = "admin@local.com"
