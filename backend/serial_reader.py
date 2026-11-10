import json
import os
import serial
import threading
import time

from dotenv import load_dotenv
from mqtt_client import client

load_dotenv()

SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyACM0")
SERIAL_BAUDRATE = int(os.getenv("SERIAL_BAUDRATE", "9600"))
MQTT_TOPIC = os.getenv(
    "MQTT_TOPIC_SENSOR",
    "iot/sensores/distancia"
)


class SerialReader:
    def __init__(self, porta=None, velocidade=9600):
        self.porta = porta or SERIAL_PORT
        self.velocidade = velocidade
        self.conexao = None
        self.ultima_leitura = None
        self.executando = False
        self.thread = None

    def conectar(self):
        try:
            self.conexao = serial.Serial(
                self.porta,
                self.velocidade,
                timeout=1
            )

            time.sleep(2)

            print(f"Arduino conectado em {self.porta}")
            return True

        except (serial.SerialException, TypeError) as erro:
            print(f"Erro ao conectar Arduino: {erro}")
            return False

    def processar_dados(self, linha):
        try:
            partes = linha.strip().split(",")

            if len(partes) != 3:
                return None

            distancia = float(partes[0])
            situacao = partes[1].strip()
            buzzer = int(partes[2])

            if distancia <= 0 or distancia > 400:
                return None

            if situacao not in ("PERIGO", "ATENCAO", "SEGURO"):
                return None

            if buzzer not in (0, 1):
                return None

            return {
                "distancia": distancia,
                "situacao": situacao,
                "buzzer": buzzer
            }

        except (ValueError, TypeError):
            return None

    def iniciar(self):
        if not self.conectar():
            return

        self.executando = True

        self.thread = threading.Thread(
            target=self._ler,
            daemon=True
        )

        self.thread.start()

    def _ler(self):
        while self.executando:
            try:
                linha = self.conexao.readline().decode(
                    "utf-8",
                    errors="ignore"
                )

                if not linha:
                    continue

                leitura = self.processar_dados(linha)

                if leitura:
                    self.ultima_leitura = leitura

                    mensagem = json.dumps({
                        "distancia_cm": leitura["distancia"],
                        "situacao": leitura["situacao"],
                        "buzzer": leitura["buzzer"]
                    })

                    resultado = client.publish(
                        MQTT_TOPIC,
                        mensagem,
                        qos=1
                    )

                    if resultado.rc == 0:
                        print("Leitura enviada ao MQTT:", leitura)
                    else:
                        print("Erro ao publicar no MQTT.")

            except (serial.SerialException, OSError) as erro:
                print("Erro na comunicação serial:", erro)
                self.executando = False

    def parar(self):
        self.executando = False

        if self.conexao and self.conexao.is_open:
            self.conexao.close()

        print("Comunicação serial encerrada")


def iniciar_serial_reader():
    leitor = SerialReader()
    leitor.iniciar()
    return leitor
