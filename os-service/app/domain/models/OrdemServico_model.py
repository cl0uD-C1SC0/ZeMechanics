from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.database import Base
from app.domain.enums.StatusOS import StatusOS
from datetime import datetime, timezone

class OrdemDeServico(Base):
    __tablename__ = "ordens_de_servico"

    id            = Column(Integer, primary_key=True, index=True)
    status        = Column(String(50), default=StatusOS.RECEBIDA)
    criado_em     = Column(DateTime, default=datetime.now(timezone.utc))
    iniciado_em   = Column(DateTime, nullable=True)   
    finalizado_em = Column(DateTime, nullable=True)   
    entregue_em   = Column(DateTime, nullable=True)
    cliente_id    = Column(Integer, ForeignKey("clientes.id"))
    veiculo_id    = Column(Integer, ForeignKey("veiculos.id"))

    cliente     = relationship("Cliente", back_populates="ordens")
    veiculo     = relationship("Veiculo", back_populates="ordens")
    os_pecas    = relationship("OSPeca", back_populates="ordem", cascade="all, delete-orphan")
    os_servicos = relationship("OSServico", back_populates="ordem", cascade="all, delete-orphan")
    historico   = relationship("HistoricoOS", back_populates="ordem", cascade="all, delete-orphan", order_by="HistoricoOS.id")

# Peças e Serviços pertencem ao catalog-service (outro banco).
# Aqui guardamos apenas o ID + uma "foto" (nome/preço) do momento em que entrou na OS.

class OSPeca(Base):
    __tablename__ = "os_pecas"

    id         = Column(Integer, primary_key=True)
    ordem_id   = Column(Integer, ForeignKey("ordens_de_servico.id"))
    peca_id    = Column(Integer, nullable=False)
    nome       = Column(String(100), nullable=False)
    preco      = Column(Float, nullable=False)
    quantidade = Column(Integer, default=1)

    ordem = relationship("OrdemDeServico", back_populates="os_pecas")

class OSServico(Base):
    __tablename__ = "os_servicos"

    id         = Column(Integer, primary_key=True)
    ordem_id   = Column(Integer, ForeignKey("ordens_de_servico.id"))
    servico_id = Column(Integer, nullable=False)
    nome       = Column(String(200), nullable=False)
    preco      = Column(Float, nullable=False)

    ordem = relationship("OrdemDeServico", back_populates="os_servicos")

class HistoricoOS(Base):
    __tablename__ = "historico_os"

    id        = Column(Integer, primary_key=True)
    ordem_id  = Column(Integer, ForeignKey("ordens_de_servico.id"))
    status    = Column(String(50), nullable=False)
    evento    = Column(String(200), nullable=False)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ordem = relationship("OrdemDeServico", back_populates="historico")
