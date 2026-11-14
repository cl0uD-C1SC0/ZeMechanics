from datetime import datetime, timezone
from app.domain.enums.StatusExecucao import StatusExecucao, STATUS_ABERTOS

COLLECTION = "execucoes"


def create_execucao(comando, db):
    agora = datetime.now(timezone.utc)
    execucao = {
        "os_id": comando["os_id"],
        "veiculo_placa": comando.get("veiculo_placa"),
        "servicos": comando.get("servicos", []),
        "status": StatusExecucao.NA_FILA.value,
        "criado_em": agora,
        "historico": [{"status": StatusExecucao.NA_FILA.value, "evento": "Entrou na fila", "data": agora}],
    }
    db[COLLECTION].insert_one(execucao)
    return get_execucao(comando["os_id"], db)


def get_execucao(os_id, db):
    return db[COLLECTION].find_one({"os_id": os_id}, {"_id": 0})


def get_fila(db):
    return list(
        db[COLLECTION]
        .find({"status": {"$in": [s.value for s in STATUS_ABERTOS]}}, {"_id": 0})
        .sort("criado_em", 1)
    )


def update_status(os_id, status, evento, db):
    db[COLLECTION].update_one(
        {"os_id": os_id},
        {
            "$set": {"status": status.value},
            "$push": {"historico": {"status": status.value, "evento": evento, "data": datetime.now(timezone.utc)}},
        },
    )
    return get_execucao(os_id, db)
