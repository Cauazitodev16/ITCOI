// ==========================================
// IOT MONITOR - SISTEMA DE PROXIMIDADE
// HC-SR04 + LED RGB + BUZZER
// Comunicação Serial com Raspberry Pi
// ==========================================

// HC-SR04
const int trigPin = 11;
const int echoPin = 12;

// LED RGB
const int redPin = 3;
const int bluePin = 5;
const int greenPin = 6;

// Buzzer
const int buzzerPin = 8;

// Limites de distância
const float limitePerigo = 45.0;
const float limiteAtencao = 65.0;

// Controle do buzzer
unsigned long ultimoBeep = 0;
const unsigned long intervaloBeep = 1000;
const unsigned long duracaoBeep = 150;

bool buzzerLigado = false;

// ==========================================
// SETUP
// ==========================================

void setup() {
  Serial.begin(9600);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);

  pinMode(buzzerPin, OUTPUT);

  digitalWrite(trigPin, LOW);

  noTone(buzzerPin);
  desligarLED();
}

// ==========================================
// LOOP PRINCIPAL
// ==========================================

void loop() {

  float distancia = medirDistancia();

  String situacao;
  unsigned long agora = millis();

  if (distancia < 0) {

    situacao = "SENSOR_ERRO";

    desligarLED();
    noTone(buzzerPin);
    buzzerLigado = false;

  }

  else if (distancia < limitePerigo) {

    situacao = "PERIGO";

    analogWrite(redPin, 255);
    analogWrite(greenPin, 0);
    analogWrite(bluePin, 0);

    tone(buzzerPin, 1000);
    buzzerLigado = true;

  }

  else if (distancia <= limiteAtencao) {

    situacao = "ATENCAO";

    analogWrite(redPin, 255);
    analogWrite(greenPin, 100);
    analogWrite(bluePin, 0);

    if (buzzerLigado) {

      if (agora - ultimoBeep >= duracaoBeep) {
        noTone(buzzerPin);
        buzzerLigado = false;
      }

    } else if (agora - ultimoBeep >= intervaloBeep) {

      tone(buzzerPin, 1000);
      ultimoBeep = agora;
      buzzerLigado = true;

    }

  }

  else {

    situacao = "SEGURO";

    analogWrite(redPin, 0);
    analogWrite(greenPin, 255);
    analogWrite(bluePin, 0);

    noTone(buzzerPin);
    buzzerLigado = false;

  }

  // Envio dos dados para o Raspberry Pi
  Serial.print(distancia, 2);
  Serial.print(",");
  Serial.print(situacao);
  Serial.print(",");
  Serial.println(buzzerLigado ? 1 : 0);

  delay(100);
}

// ==========================================
// MEDIR DISTÂNCIA
// ==========================================

float medirDistancia() {

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);

  digitalWrite(trigPin, LOW);

  long tempo = pulseIn(echoPin, HIGH, 30000);

  if (tempo == 0) {
    return -1;
  }

  return tempo / 58.0;
}

// ==========================================
// DESLIGAR LED RGB
// ==========================================

void desligarLED() {

  analogWrite(redPin, 0);
  analogWrite(greenPin, 0);
  analogWrite(bluePin, 0);

}