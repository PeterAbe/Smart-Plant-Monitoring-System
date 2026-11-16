
const moistureValue = document.getElementById("moisture-value");
const pumpStatus = document.getElementById("pump-status");
const lastWatered = document.getElementById("last-watered");

const automaticMode = document.getElementById("automatic-mode");
const moistureThreshold = document.getElementById("moisture-threshold");
const wateringDuration = document.getElementById("watering-duration");

const waterButton = document.querySelector(".water-button");
const saveButton = document.querySelector(".save-button");



automaticMode.addEventListener("change", function () {

    if (automaticMode.checked) {
        alert("Automatic watering enabled");
    } else {
        alert("Automatic watering disabled");
    }

});




saveButton.addEventListener("click", function () {

    const threshold = Number(moistureThreshold.value);
    const duration = Number(wateringDuration.value);

    if (threshold < 0 || threshold > 100 || moistureThreshold.value === "") {
        alert("Moisture threshold must be between 0 and 100.");
        return;
    }

    if (duration < 1 || duration > 60 || wateringDuration.value === "") {
        alert("Watering duration must be between 1 and 60 seconds.");
        return;
    }

    alert(
        "Settings saved!\n" +
        "Moisture Threshold: " + threshold + "%\n" +
        "Watering Duration: " + duration + " seconds"
    );

});

document.getElementById('manual-water-btn').addEventListener('click', function() {
    const durationValue = document.getElementById('watering-duration').value;
    fetch('/api/manual-water', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ duration: parseInt(durationValue) })
    })
    .then(response => response.json())
    .then(data => {
        if(data.status === "success") {
            alert("Pump started successfully for " + durationValue + " seconds!");
        }
    })
    .catch(error => console.error('Error:', error));
});






