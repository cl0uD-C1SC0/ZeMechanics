import mongomock
import pytest

from app.main import app
from app.database import get_db

# MongoDB em memória para os testes (não precisa de um Mongo rodando)
MONGO = mongomock.MongoClient()
TEST_DB = "test_execution_db"


def override_get_db():
    return MONGO[TEST_DB]


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    yield MONGO[TEST_DB]
    MONGO.drop_database(TEST_DB)
