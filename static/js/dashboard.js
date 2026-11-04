
const moistureValue = document.getElementById("moisture-value");
const pumpStatus = document.getElementById("pump-status");
const lastWatered = document.getElementById("last-watered");

const automaticMode = document.getElementById("automatic-mode");
const moistureThreshold = document.getElementById("moisture-threshold");
const wateringDuration = document.getElementById("watering-duration");

const waterButton = document.querySelector(".water-button");
const saveButton = document.querySelector(".save-button");


function updateDashboard() {

    const sampleMoisture = 45;

    moistureValue.textContent = sampleMoisture + "%";

}


automaticMode.addEventListener("change", function () {

    if (automaticMode.checked) {
        alert("Automatic watering enabled");
    } else {
        alert("Automatic watering disabled");
    }

});


waterButton.addEventListener("click", function () {

    if (pumpStatus.textContent === "ON") {
        alert("The water pump is already running.");
        return;
    }

    const confirmWatering = confirm("Do you want to water the plant?");

    if (confirmWatering) {

        pumpStatus.textContent = "ON";

        alert("Manual watering requested.");

    

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




updateDashboard();
