const distanceElement = document.getElementById("distance");
const updateElement = document.getElementById("lastUpdate");
const countElement = document.getElementById("readingCount");
const messageElement = document.getElementById("distanceMessage");
const historyBody = document.getElementById("historyBody");

const history = [];
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

function registerReading(distance) {
    const now = new Date();
    const time = now.toLocaleTimeString("pt-BR");

    distanceElement.textContent = distance.toFixed(2);
    updateElement.textContent = time;
    messageElement.textContent =
        distance < 20 ? "Objeto próximo" : "Leitura registrada";

    history.unshift({
        time,
        distance: distance.toFixed(2)
    });

    if (history.length > maxReadings) {
        history.pop();
    }

    countElement.textContent = history.length;

    chart.data.labels.push(time);
    chart.data.datasets[0].data.push(distance);

    if (chart.data.labels.length > maxReadings) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }

    chart.update();
    renderHistory();
}

function renderHistory() {
    if (history.length === 0) {
        historyBody.innerHTML =
            '<tr><td colspan="3">Nenhuma leitura registrada.</td></tr>';
        return;
    }

    historyBody.innerHTML = history.map(item => `
        <tr>
            <td>${item.time}</td>
            <td>${item.distance} cm</td>
            <td>${Number(item.distance) < 20 ? "Objeto próximo" : "Normal"}</td>
        </tr>
    `).join("");
}

// Dados simulados para testar o painel.
function simulateReading() {
    const distance = Math.random() * 100;
    registerReading(distance);
}

simulateReading();
setInterval(simulateReading, 3000);

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

// Limpar o histórico visual.
document.getElementById("clearHistory").addEventListener("click", () => {
    history.length = 0;

    chart.data.labels = [];
    chart.data.datasets[0].data = [];
    chart.update();

    countElement.textContent = "0";
    distanceElement.textContent = "--";
    updateElement.textContent = "--:--:--";
    messageElement.textContent = "Aguardando leitura";

    renderHistory();
});