from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
from database import engine, get_db
from schemas import (
    LeituraCreate,
    LeituraResponse,
    ComandoCreate
)
from repository import (
    salvar_leitura,
    listar_leituras,
    buscar_ultima_leitura,
    listar_sensores,
    listar_logs
)
from mqtt_client import (
    iniciar_mqtt,
    parar_mqtt,
    publicar_comando,
    client
)
from serial_reader import iniciar_serial_reader


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)

    iniciar_mqtt()
    iniciar_serial_reader()

    yield

    parar_mqtt()


app = FastAPI(
    title="IoT Monitor API",
    description="API de monitoramento e controle do projeto IoT.",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def inicio():
    return {
        "mensagem": "IoT Monitor API funcionando!",
        "documentacao": "/docs"
    }


@app.get("/status")
def status():
    return {
        "api": "online",
        "mqtt": "conectado" if client.is_connected() else "desconectado"
    }


@app.get("/leituras", response_model=list[LeituraResponse])
def obter_leituras(
    limite: int = 50,
    db: Session = Depends(get_db)
):
    if limite < 1 or limite > 500:
        raise HTTPException(
            status_code=400,
            detail="O limite deve estar entre 1 e 500."
        )

    return listar_leituras(db, limite)


@app.get("/leituras/ultima", response_model=LeituraResponse)
def obter_ultima_leitura(db: Session = Depends(get_db)):
    leitura = buscar_ultima_leitura(db)

    if leitura is None:
        raise HTTPException(
            status_code=404,
            detail="Nenhuma leitura encontrada."
        )

    return leitura


@app.post("/leituras", response_model=LeituraResponse)
def criar_leitura(
    dados: LeituraCreate,
    db: Session = Depends(get_db)
):
    if dados.distancia_cm < 0:
        raise HTTPException(
            status_code=400,
            detail="A distância não pode ser negativa."
        )

    return salvar_leitura(
        db=db,
        valor=dados.distancia_cm,
        nome="Sensor de Distância",
        tipo="Ultrassônico HC-SR04",
        unidade="cm",
        topico="iot/sensores/distancia"
    )


@app.get("/sensores")
def obter_sensores(db: Session = Depends(get_db)):
    return listar_sensores(db)


@app.get("/logs")
def obter_logs(
    limite: int = 50,
    db: Session = Depends(get_db)
):
    if limite < 1 or limite > 500:
        raise HTTPException(
            status_code=400,
            detail="O limite deve estar entre 1 e 500."
        )

    return listar_logs(db, limite)


@app.post("/comandos/{atuador}")
def enviar_comando(atuador: str, dados: ComandoCreate):

    if atuador not in ["buzzer", "servo"]:
        raise HTTPException(
            status_code=400,
            detail="Atuador não reconhecido."
        )

    if atuador == "buzzer":
        if dados.estado not in ["ligado", "desligado"]:
            raise HTTPException(
                status_code=400,
                detail="Informe estado como ligado ou desligado."
            )

        mensagem = {"estado": dados.estado}

    else:
        if dados.posicao is None or not 0 <= dados.posicao <= 180:
            raise HTTPException(
                status_code=400,
                detail="A posição do servo deve estar entre 0 e 180."
            )

        mensagem = {"posicao": dados.posicao}

    topico = f"iot/atuadores/{atuador}/comando"

    publicado = publicar_comando(topico, mensagem)

    if not publicado:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível enviar o comando. MQTT desconectado."
        )

    return {
        "mensagem": "Comando enviado!",
        "atuador": atuador,
        "topico": topico,
        "dados": mensagem
    }
