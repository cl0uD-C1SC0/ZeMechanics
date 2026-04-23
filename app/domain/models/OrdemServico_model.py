from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from app.domain.enums.status_os import StatusOS
from datetime import datetime

class OrdemDeServico(Base):
    __tablename__ = "ordens_de_servico"

    id         = Column(Integer, primary_key=True, index=True)
    status     = Column(String(50), default=StatusOS.RECEBIDA)
    criado_em  = Column(DateTime, default=datetime.utcnow)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    veiculo_id = Column(Integer, ForeignKey("veiculos.id"))

    cliente  = relationship("Cliente", back_populates="ordens")
    veiculo  = relationship("Veiculo", back_populates="ordens")
    pecas    = relationship("Peca", secondary="os_pecas", backref="ordens")
    servicos = relationship("Servicos", secondary="os_servicos", backref="ordens") #


class OSPeca(Base):
    __tablename__ = "os_pecas"

    id         = Column(Integer, primary_key=True)
    ordem_id   = Column(Integer, ForeignKey("ordens_de_servico.id"))
    peca_id    = Column(Integer, ForeignKey("pecas.id"))
    quantidade = Column(Integer, default=1)

class OSServico(Base):
    __tablename__ = "os_servicos"

    id         = Column(Integer, primary_key=True)
    ordem_id   = Column(Integer, ForeignKey("ordens_de_servico.id"))
    servico_id = Column(Integer, ForeignKey("servicos.id"))