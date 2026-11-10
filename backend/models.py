from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Sensor(Base):
    __tablename__ = "sensores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)
    unidade = Column(String(20), nullable=False)
    topico_mqtt = Column(String(150), unique=True, nullable=False)

    leituras = relationship("Leitura", back_populates="sensor")


class Leitura(Base):
    __tablename__ = "leituras"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensores.id"), nullable=False)
    valor = Column(Float, nullable=False)
    recebido_em = Column(DateTime, default=datetime.now)

    sensor = relationship("Sensor", back_populates="leituras")


class LogSistema(Base):
    __tablename__ = "logs_sistema"

    id = Column(Integer, primary_key=True, index=True)
    nivel = Column(String(20), nullable=False)
    mensagem = Column(String(255), nullable=False)
    criado_em = Column(DateTime, default=datetime.now)
