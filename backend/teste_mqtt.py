import paho.mqtt.client as mqtt
import json
import time

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

def on_connect(client, userdata, flags, reason_code, properties):
    print("Conectado ao broker!")

try:
    client.on_connect = on_connect

    client.connect("192.168.137.83", 1883, 60)
    client.loop_start()

    time.sleep(2)

    distancias = [45.5, 32.0, 20.5, 15.0, 8.5]

    for distancia in distancias:
        mensagem = json.dumps({
            "distancia_cm": distancia
        })

        resultado = client.publish(
            "iot/sensores/distancia",
            mensagem,
            qos=1
        )

        resultado.wait_for_publish(timeout=10)

        print(f"Enviado: {distancia} cm")
        time.sleep(2)

except Exception as erro:
    print(f"Erro: {erro}")

finally:
    if client.is_connected():
        client.disconnect()

    client.loop_stop()
