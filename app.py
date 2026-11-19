from flask import Flask, redirect, url_for, render_template, request, jsonify
from datetime import datetime, timedelta, timezone
from database.models import get_dashboard_settings, get_latest_reading, get_readings, update_dashboard_settings
from services.watering import manual_watering


# Initialize the Flask application
app = Flask(__name__)


live_plant_data = {
    "moisture": 20,
    "temperature": 22.4,
    "humidity": 55,
    "pump_status": "OFF",
    "last_watered": "Today at 02:14 PM"
}


# Homepage
@app.route('/')
def home():
    return redirect(url_for("dashboard"))


# Dashboard
@app.route('/dashboard')
def dashboard():
    latest_reading = get_latest_reading()
    system_settings = get_dashboard_settings()

    if latest_reading:
        live_plant_data["moisture"] = latest_reading["moisture"]
        live_plant_data["temperature"] = latest_reading["temperature"]
        live_plant_data["humidity"] = latest_reading["humidity"]

    return render_template(
        "dashboard.html",
        plant_data=live_plant_data,
        system_settings=system_settings
    )

@app.route('/api/moisture-history')
def api_moisture_history():
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=24)

    readings = get_readings(
        start_time=start_time,
        end_time=end_time,
        limit=1000
    )

    history = [
        {
            "timestamp": reading["timestamp"],
            "moisture": reading["moisture"]
        }
        for reading in readings
    ]

    return jsonify(history)

# Save dashboard settings
@app.route('/save-settings', methods=['POST'])
def save_settings():
    threshold = int(request.form.get("moisture_threshold", 30))
    duration = int(request.form.get("watering_duration", 5))
    automatic_mode = "automatic_mode" in request.form

    update_dashboard_settings(
        moisture_threshold=threshold,
        watering_duration=duration,
        automatic_watering_enabled=automatic_mode
    )

    return redirect(url_for("dashboard"))


# Manual watering API
@app.route('/api/manual-water', methods=['POST'])
def api_manual_water():
    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "No watering data received."
        }), 400

    duration = data.get("duration", 5)

    try:
        manual_watering(duration)
    except ValueError as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400

    return jsonify({
        "status": "success",
        "message": f"Pump activated for {duration} seconds."
    })
