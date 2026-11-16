from flask import Flask, redirect, url_for, render_template, request, jsonify
import os
#from hardware.moisture_sensor import *
#from hardware.water_pump import *
#from services.watering import *

# Initialize the Flask application
app = Flask(__name__)


#current_moisture = Read_Moisture

system_settings = {
    "threshold": 25,
    "duration": 5,
    "auto_mode": True
}

live_plant_data = {
    "moisture": 20,
    "temperature": 22.4,
    "humidity": 55,
    "pump_status": "OFF",
    "last_watered": "Today at 02:14 PM"
}


# Define a route for the homepage
@app.route('/')
def home():
    return redirect(url_for("dashboard"))

@app.route('/dashboard')
def dashboard():
    return render_template(
        "dashboard.html",
        plant_data=live_plant_data, 
        system_settings=system_settings)
    
@app.route('/save-settings', methods=['POST'])
def save_settings():
    system_settings["threshold"] = int(request.form.get("moisture_threshold", 25))
    system_settings["duration"] = int(request.form.get("watering_duration", 5))
    
    system_settings["auto_mode"] = "automatic_mode" in request.form
    
    print(f"Updated System Settings: {system_settings}") 
    
    return redirect(url_for("dashboard"))

#@app.route('/api/manual-water', methods=['POST'])
#def api_manual_water():
    #data = request.get_json()
    #duration = data.get('duration', 5)  # Default to 5 seconds if none found
    #manual_watering(duration)
    
    # Instantly reply to the browser so the UI stays super responsive
    #return jsonify({"status": "success", "message": f"Pump activated for {duration}s"})

