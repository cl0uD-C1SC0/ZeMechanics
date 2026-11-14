from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
from app.domain.enums.StatusOrcamento import StatusOrcamento

# O billing NÃO acessa o banco do os-service: tudo que ele precisa saber da OS
# (cliente, itens, total) chega na mensagem GERAR_ORCAMENTO e é guardado aqui.

class Orcamento(Base):
    __tablename__ = "orcamentos"

    id            = Column(Integer, primary_key=True, index=True)
    os_id         = Column(Integer, unique=True, nullable=False, index=True)
    cliente_nome  = Column(String(100), nullable=False)
    cliente_email = Column(String(100), nullable=False)
    cliente_cpf   = Column(String(14), nullable=False)
    itens         = Column(JSON, nullable=False)
    valor_total   = Column(Float, nullable=False)
    status        = Column(String(30), default=StatusOrcamento.AGUARDANDO_APROVACAO)
    criado_em     = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    pagamentos = relationship("Pagamento", back_populates="orcamento", order_by="Pagamento.id")

# Cada movimento financeiro é uma linha nova (aprovado, recusado, estornado).
# Estorno não apaga o pagamento: é um novo lançamento.

class Pagamento(Base):
    __tablename__ = "pagamentos"

    id           = Column(Integer, primary_key=True)
    orcamento_id = Column(Integer, ForeignKey("orcamentos.id"))
    valor        = Column(Float, nullable=False)
    status       = Column(String(20), nullable=False)
    gateway_id   = Column(String(100), nullable=False)
    criado_em    = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    orcamento = relationship("Orcamento", back_populates="pagamentos")
