from pydantic import BaseModel, ConfigDict
from datetime import datetime


class LeituraCreate(BaseModel):
    distancia_cm: float


class SensorResponse(BaseModel):
    id: int
    nome: str
    tipo: str
    unidade: str
    topico_mqtt: str

    model_config = ConfigDict(from_attributes=True)


class LeituraResponse(BaseModel):
    id: int
    sensor_id: int
    valor: float
    recebido_em: datetime

    model_config = ConfigDict(from_attributes=True)


class ComandoCreate(BaseModel):
    estado: str | None = None
    posicao: int | None = None
