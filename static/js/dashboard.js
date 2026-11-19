const moistureValue = document.getElementById("moisture-value");
const pumpStatus = document.getElementById("pump-status");
const lastWatered = document.getElementById("last-watered");

const automaticMode = document.getElementById("automatic-mode");
const moistureThreshold = document.getElementById("moisture-threshold");
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
        alert(data.message);
    })
    .catch(error => {
        alert(error.message);
        console.error('Error:', error);
    });

});


// Moisture history chart
const chartCanvas = document.getElementById("moisture-chart");
const chartMessage = document.getElementById("chart-message");

if (chartCanvas) {

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

            new Chart(chartCanvas, {
                type: 'line',

                data: {
                    labels: readings.map(reading =>
                        new Date(reading.timestamp).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit'
                        })
                    ),

                    datasets: [{
                        label: 'Soil Moisture (%)',
                        data: readings.map(reading => reading.moisture),
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
        })
        .catch(error => {
            console.error("Chart error:", error);

            chartCanvas.style.display = "none";
            chartMessage.textContent = "Unable to load moisture history.";
            chartMessage.style.display = "block";
        });
}
