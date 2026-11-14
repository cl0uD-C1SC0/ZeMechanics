from pymongo import MongoClient
from app.core.config import settings

# Banco NÃO relacional (MongoDB): cada execução é um documento com o seu
# histórico embutido — não precisa de JOIN nem de tabelas auxiliares.

client = MongoClient(settings.MONGO_URL, serverSelectionTimeoutMS=3000)


def get_db():
    return client[settings.MONGO_DB]
