from pymongo.errors import PyMongoError


def verificar_liveness():
    return {"status": "ok"}


def verificar_readiness(db):
    try:
        db.command("ping")
    except PyMongoError:
        return False
    return True
