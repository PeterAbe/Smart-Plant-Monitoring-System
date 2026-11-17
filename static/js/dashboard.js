
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
