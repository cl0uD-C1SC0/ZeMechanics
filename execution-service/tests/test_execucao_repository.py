from app.repositories import ExecucaoRepository
from app.domain.enums.StatusExecucao import StatusExecucao

COMANDO = {"tipo": "EXECUTAR_OS", "os_id": 1, "veiculo_placa": "ABC1D23", "servicos": ["Troca de Óleo"]}


def test_create_execucao_entra_na_fila(db):
    execucao = ExecucaoRepository.create_execucao(COMANDO, db)

    assert execucao["os_id"] == 1
    assert execucao["status"] == "Na Fila"
    assert execucao["servicos"] == ["Troca de Óleo"]
    assert execucao["historico"][0]["evento"] == "Entrou na fila"
    assert "_id" not in execucao


def test_get_execucao_inexistente(db):
    assert ExecucaoRepository.get_execucao(99, db) is None


def test_update_status_guarda_historico(db):
    ExecucaoRepository.create_execucao(COMANDO, db)

    execucao = ExecucaoRepository.update_status(1, StatusExecucao.EM_DIAGNOSTICO, "Avanço do mecânico", db)

    assert execucao["status"] == "Em Diagnóstico"
    assert [h["status"] for h in execucao["historico"]] == ["Na Fila", "Em Diagnóstico"]


def test_fila_mostra_so_abertas_em_ordem(db):
    ExecucaoRepository.create_execucao({**COMANDO, "os_id": 1}, db)
    ExecucaoRepository.create_execucao({**COMANDO, "os_id": 2}, db)
    ExecucaoRepository.create_execucao({**COMANDO, "os_id": 3}, db)
    ExecucaoRepository.update_status(2, StatusExecucao.FINALIZADA, "fim", db)
    ExecucaoRepository.update_status(3, StatusExecucao.EM_REPARO, "reparo", db)

    fila = ExecucaoRepository.get_fila(db)

    assert [e["os_id"] for e in fila] == [1, 3]
