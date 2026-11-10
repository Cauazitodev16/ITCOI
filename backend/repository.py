from sqlalchemy.orm import Session
from models import Sensor, Leitura, LogSistema


def registrar_log(db: Session, nivel: str, mensagem: str):
    log = LogSistema(
        nivel=nivel,
        mensagem=mensagem
    )

    db.add(log)
    db.commit()

    return log


def salvar_leitura(
    db: Session,
    valor: float,
    nome: str,
    tipo: str,
    unidade: str,
    topico: str
):
    sensor = db.query(Sensor).filter(
        Sensor.topico_mqtt == topico
    ).first()

    if sensor is None:
        sensor = Sensor(
            nome=nome,
            tipo=tipo,
            unidade=unidade,
            topico_mqtt=topico
        )

        db.add(sensor)
        db.commit()
        db.refresh(sensor)

    leitura = Leitura(
        sensor_id=sensor.id,
        valor=valor
    )

    db.add(leitura)
    db.commit()
    db.refresh(leitura)

    return leitura


def listar_leituras(db: Session, limite: int = 50):
    return (
        db.query(Leitura)
        .order_by(Leitura.recebido_em.desc())
        .limit(limite)
        .all()
    )


def buscar_ultima_leitura(db: Session):
    return (
        db.query(Leitura)
        .order_by(Leitura.recebido_em.desc())
        .first()
    )


def listar_sensores(db: Session):
    return db.query(Sensor).all()


def listar_logs(db: Session, limite: int = 50):
    return (
        db.query(LogSistema)
        .order_by(LogSistema.criado_em.desc())
        .limit(limite)
        .all()
    )
