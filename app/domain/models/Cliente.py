from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id       = Column(Integer, primary_key=True, index=True)
    nome     = Column(String(100), nullable=False)
    cpf      = Column(String(14), unique=True, nullable=False)
    contato  = Column(String(20), nullable=False)
    endereco = Column(String(200), nullable=False)

    veiculos = relationship("Veiculo", back_populates="cliente") 
    
