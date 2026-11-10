import json
import os

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from database import SessionLocal
from repository import salvar_leitura, registrar_log

load_dotenv()

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv(
    "MQTT_TOPIC_SENSOR",
    "iot/sensores/distancia"
)

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="iot-monitor-backend"
)


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Conectado ao broker MQTT!")
        client.subscribe(MQTT_TOPIC)
        print(f"Inscrito no tópico: {MQTT_TOPIC}")
    else:
        print(f"Falha na conexão MQTT: {reason_code}")


def on_message(client, userdata, message):
    db = SessionLocal()

    try:
        conteudo = message.payload.decode("utf-8")
        dados = json.loads(conteudo)

        distancia = dados.get("distancia_cm")

        if distancia is None:
            print("Mensagem sem distância válida.")
            return

        distancia = float(distancia)

        if distancia < 0:
            print("Distância inválida.")
            return

        salvar_leitura(
            db=db,
            valor=distancia,
            nome="Sensor de Distância",
            tipo="Ultrassônico HC-SR04",
            unidade="cm",
            topico=message.topic
        )

        print(f"Distância recebida: {distancia} cm")

    except (ValueError, TypeError, json.JSONDecodeError) as erro:
        registrar_log(db, "ERRO", f"Mensagem MQTT inválida: {erro}")
        print(f"Erro ao processar mensagem: {erro}")

    except Exception as erro:
        print(f"Erro ao salvar leitura: {erro}")

    finally:
        db.close()


client.on_connect = on_connect
client.on_message = on_message


def iniciar_mqtt():
    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_start()
        return True

    except Exception as erro:
        print(f"Não foi possível conectar ao MQTT: {erro}")
        return False


def parar_mqtt():
    if client.is_connected():
        client.disconnect()

    client.loop_stop()


def publicar_comando(topico: str, dados: dict):
    if not client.is_connected():
        return False

    mensagem = json.dumps(dados)

    resultado = client.publish(topico, mensagem)

    return resultado.rc == mqtt.MQTT_ERR_SUCCESS
