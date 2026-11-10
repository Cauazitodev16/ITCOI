INSERT OR IGNORE INTO sensores (
    nome,
    tipo,
    unidade,
    topico_mqtt
) VALUES (
    'Sensor de Distancia',
    'Ultrassonico HC-SR04',
    'cm',
    'iot/sensores/distancia'
);
