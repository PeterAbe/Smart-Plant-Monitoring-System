
const moistureValue = document.getElementById("moisture-value");
const temperatureValue = document.getElementById("temperature-value");
const humidityValue = document.getElementById("humidity-value");
const pumpStatus = document.getElementById("pump-status");
const lastWatered = document.getElementById("last-watered");
const wateringMode = document.getElementById("watering-mode");

const wateringDuration = document.getElementById("watering-duration");
const waterButton = document.getElementById("manual-water-btn");


// Manual watering
waterButton.addEventListener("click", function () {

    const durationValue = Number(wateringDuration.value);

    if (
        !Number.isInteger(durationValue) ||
        durationValue < 1 ||
        durationValue > 30
    ) {
        alert("Watering duration must be between 1 and 30 seconds.");
        return;
    }

    fetch('/api/manual-water', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            duration: durationValue
        })
    })
    .then(async response => {
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "Unable to start watering.");
        }

        return data;
    })
    .then(data => {
        console.log(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
    });

});


// Automatically update dashboard information
function updateDashboard() {

    fetch('/api/dashboard-data')
        .then(response => {
            if (!response.ok) {
                throw new Error("Unable to load dashboard data.");
            }

            return response.json();
        })
        .then(data => {

            if (data.moisture !== null) {
                moistureValue.textContent = data.moisture + "%";
            }

            temperatureValue.textContent =
                data.temperature !== null
                    ? data.temperature + "°C"
                    : "--";

            humidityValue.textContent =
                data.humidity !== null
                    ? data.humidity + "%"
                    : "--";

            pumpStatus.textContent = data.pump_status;
            lastWatered.textContent = data.last_watered;
            wateringMode.textContent = data.watering_mode;

        })
        .catch(error => {
            console.error("Dashboard update error:", error);
        });
}


// Moisture history chart
const chartCanvas = document.getElementById("moisture-chart");
const chartMessage = document.getElementById("chart-message");

let moistureChart = null;

function updateMoistureChart() {

    if (!chartCanvas) {
        return;
    }

    fetch('/api/moisture-history')
        .then(response => {
            if (!response.ok) {
                throw new Error("Unable to load moisture history.");
            }

            return response.json();
        })
        .then(readings => {

            if (readings.length === 0) {
                chartCanvas.style.display = "none";
                chartMessage.style.display = "block";
                return;
            }

            chartCanvas.style.display = "block";
            chartMessage.style.display = "none";

            const labels = readings.map(reading =>
                new Date(reading.timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                })
            );

            const moistureData = readings.map(reading => reading.moisture);

            if (moistureChart === null) {

                moistureChart = new Chart(chartCanvas, {
                    type: 'line',

                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Soil Moisture (%)',
                            data: moistureData,
                            borderWidth: 2,
                            tension: 0.3,
                            fill: false
                        }]
                    },

                    options: {
                        responsive: true,
                        maintainAspectRatio: false,

                        scales: {
                            y: {
                                min: 0,
                                max: 100,
                                title: {
                                    display: true,
                                    text: 'Moisture (%)'
                                }
                            },

                            x: {
                                title: {
                                    display: true,
                                    text: 'Time'
                                }
                            }
                        }
                    }
                });

            } else {

                moistureChart.data.labels = labels;
                moistureChart.data.datasets[0].data = moistureData;
                moistureChart.update();

            }

        })
        .catch(error => {
            console.error("Chart error:", error);
            chartMessage.textContent = "Unable to load moisture history.";
            chartMessage.style.display = "block";
        });
}


// Initial updates
updateDashboard();
updateMoistureChart();

// Automatic refresh intervals
setInterval(updateDashboard, 2000);
setInterval(updateMoistureChart, 10000);
