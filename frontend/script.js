const API_URL = "http://127.0.0.1:8000";

const distanceElement = document.getElementById("distance");
const updateElement = document.getElementById("lastUpdate");
const countElement = document.getElementById("readingCount");
const messageElement = document.getElementById("distanceMessage");
const historyBody = document.getElementById("historyBody");
const connectionStatus = document.getElementById("connectionStatus");
const statusDot = document.querySelector(".status-dot");

const maxReadings = 20;

const chart = new Chart(
    document.getElementById("distanceChart"),
    {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "Distância (cm)",
                data: [],
                borderColor: "#ef3038",
                backgroundColor: "rgba(239, 48, 56, 0.12)",
                fill: true,
                tension: 0.3,
                pointRadius: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: "#f5f5f5" }
                }
            },
            scales: {
                x: {
                    ticks: { color: "#a1a1aa" },
                    grid: { color: "#303137" }
                },
                y: {
                    beginAtZero: true,
                    ticks: { color: "#a1a1aa" },
                    grid: { color: "#303137" },
                    title: {
                        display: true,
                        text: "Centímetros",
                        color: "#a1a1aa"
                    }
                }
            }
        }
    }
);

function formatTime(dateString) {
    const date = new Date(dateString);

    if (Number.isNaN(date.getTime())) {
        return "--:--:--";
    }

    return date.toLocaleTimeString("pt-BR");
}

function updateConnectionStatus(text, color) {
    connectionStatus.textContent = text;
    statusDot.style.backgroundColor = color;
}

function renderHistory(readings) {
    if (readings.length === 0) {
        historyBody.innerHTML =
            '<tr><td colspan="3">Nenhuma leitura registrada.</td></tr>';
        return;
    }

    historyBody.innerHTML = readings.map(item => {
        const distance = Number(item.valor);
        const time = formatTime(item.recebido_em);

        return `
            <tr>
                <td>${time}</td>
                <td>${distance.toFixed(2)} cm</td>
                <td>${distance < 20 ? "Objeto próximo" : "Normal"}</td>
            </tr>
        `;
    }).join("");
}

async function loadReadings() {
    try {
        const response = await fetch(
            `${API_URL}/leituras?limite=${maxReadings}`,
            { cache: "no-store" }
        );

        if (!response.ok) {
            throw new Error("Erro ao buscar leituras.");
        }

        const readings = await response.json();

        countElement.textContent = readings.length;

        if (readings.length === 0) {
            distanceElement.textContent = "--";
            updateElement.textContent = "--:--:--";
            messageElement.textContent = "Aguardando leitura";

            chart.data.labels = [];
            chart.data.datasets[0].data = [];
            chart.update();

            renderHistory([]);
            return;
        }

        const latestReading = readings[0];
        const distance = Number(latestReading.valor);

        distanceElement.textContent = distance.toFixed(2);
        updateElement.textContent = formatTime(
            latestReading.recebido_em
        );

        messageElement.textContent =
            distance < 20 ? "Objeto próximo" : "Leitura registrada";

        renderHistory(readings);

        // A API retorna as leituras da mais recente para a mais antiga.
        // Para o gráfico, colocamos em ordem cronológica.
        const chronologicalReadings = [...readings].reverse();

        chart.data.labels = chronologicalReadings.map(
            item => formatTime(item.recebido_em)
        );

        chart.data.datasets[0].data = chronologicalReadings.map(
            item => Number(item.valor)
        );

        chart.update();

    } catch (error) {
        console.error("Erro ao carregar leituras:", error);
        messageElement.textContent = "Não foi possível carregar os dados.";
        throw error;
    }
}

async function checkConnection() {
    try {
        const response = await fetch(`${API_URL}/status`);

        if (!response.ok) {
            throw new Error("API indisponível.");
        }

        const status = await response.json();

        const mqttStatus = status.mqtt === "conectado"
            ? "MQTT conectado"
            : "MQTT desconectado";

        updateConnectionStatus(
            `API online · ${mqttStatus}`,
            "#22c55e"
        );

    } catch (error) {
        updateConnectionStatus("API desconectada", "#ef3038");
    }
}

async function updateDashboard() {
    await checkConnection();

    try {
        await loadReadings();
    } catch (error) {
        // O erro já foi tratado e registrado em loadReadings().
    }
}

// Atualiza o painel assim que a página abre.
updateDashboard();

// Atualiza os dados automaticamente a cada 3 segundos.
setInterval(updateDashboard, 3000);

// Controle demonstrativo do buzzer.
let buzzerOn = false;

document.getElementById("buzzerButton").addEventListener("click", () => {
    buzzerOn = !buzzerOn;

    document.getElementById("buzzerStatus").textContent =
        buzzerOn ? "Ligado (simulado)" : "Desligado";

    document.getElementById("buzzerButton").textContent =
        buzzerOn ? "Desligar" : "Ligar";
});

// Controle demonstrativo do servo motor.
let servoPosition = 0;

document.getElementById("servoButton").addEventListener("click", () => {
    servoPosition = servoPosition === 0 ? 90 : 0;

    document.getElementById("servoStatus").textContent =
        `Posição: ${servoPosition}° (simulada)`;
});

// Atualiza o histórico manualmente.
document.getElementById("clearHistory").addEventListener("click", () => {
    updateDashboard();
});