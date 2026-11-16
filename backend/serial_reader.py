
import os
import re
import time
import threading

import serial
from dotenv import load_dotenv

from mqtt_client import client

# Carrega as configurações do arquivo .env
load_dotenv()

SERIAL_PORT = os.getenv("SERIAL_PORT", "COM7")
SERIAL_BAUDRATE = int(os.getenv("SERIAL_BAUDRATE", "9600"))

MQTT_TOPIC = os.getenv(
    "MQTT_TOPIC_SENSOR",
    "iot/sensores/distancia"
)


class SerialReader:

    def __init__(self, porta=None, velocidade=None):
        self.porta = porta or SERIAL_PORT
        self.velocidade = velocidade or SERIAL_BAUDRATE

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

            # Aguarda a inicialização da comunicação serial
            time.sleep(2)

            print(f"Arduino conectado em {self.porta}")
            return True

        except serial.SerialException as erro:
            print(f"Erro ao conectar com o Arduino: {erro}")
            return False

    def processar_dados(self, linha):
        try:
            # Formato esperado:
            # Distancia: 25.50 cm - SEGURO

            resultado = re.search(
                r"Distancia:\s*([\d.]+)\s*cm\s*-\s*(PERIGO|ATENCAO|SEGURO)",
                linha,
                re.IGNORECASE
            )

            if not resultado:
                return None

            distancia = float(resultado.group(1))
            situacao = resultado.group(2).upper()

            if distancia <= 0 or distancia > 400:
                return None

            return {
                "distancia": distancia,
                "situacao": situacao,
                "buzzer": 0
            }

        except (ValueError, TypeError):
            return None

    def iniciar(self):
        if self.executando:
            return

        if not self.conectar():
            return

        self.executando = True

        self.thread = threading.Thread(
            target=self._ler,
            daemon=True
        )

        self.thread.start()

        print("Leitor serial iniciado. Aguardando leituras...")

    def _ler(self):
        while self.executando:
            try:
                linha = self.conexao.readline().decode(
                    "utf-8",
                    errors="ignore"
                ).strip()

                if not linha:
                    continue

                leitura = self.processar_dados(linha)

                if leitura is None:
                    continue

                self.ultima_leitura = leitura

                mensagem = {
                    "distancia_cm": leitura["distancia"],
                    "situacao": leitura["situacao"],
                    "buzzer": leitura["buzzer"]
                }

                import json
                resultado = client.publish(
                    MQTT_TOPIC,
                    json.dumps(mensagem),
                    qos=1
                )

                if resultado.rc == 0:
                    print(
                        f"Distância: {leitura['distancia']:.2f} cm | "
                        f"Situação: {leitura['situacao']} | "
                        f"Enviada ao MQTT"
                    )
                else:
                    print("Erro ao publicar leitura no MQTT.")

            except (serial.SerialException, OSError) as erro:
                print(f"Erro na comunicação serial: {erro}")
                self.executando = False

    def parar(self):
        self.executando = False

        if self.conexao and self.conexao.is_open:
            self.conexao.close()

        print("Comunicação serial encerrada.")


def iniciar_serial_reader():
    leitor = SerialReader()
    leitor.iniciar()
    return leitor
