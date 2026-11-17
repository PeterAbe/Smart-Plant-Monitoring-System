import time, threading
from hardware.moisture_sensor import read_moisture
from database.models import add_sensor_reading, get_dashboard_settings
from .watering import manual_watering
import config

last_logged_time = 0
last_automatic_watering_time = 0

def get_moisture_reading():
    moisture = read_moisture()
    return moisture


def save_moisture_reading(moisture):
    add_sensor_reading(moisture=moisture)


def confirm_low_moisture(first_reading):
    readings = [first_reading]

    time.sleep(1)
    second_reading = get_moisture_reading()
    readings.append(second_reading)

    time.sleep(1)
    third_reading = get_moisture_reading()
    readings.append(third_reading)

    for reading in readings:
        save_moisture_reading(reading)

    average_moisture = sum(readings) / len(readings)

    return average_moisture


def check_watering_condition(average_moisture):
    settings = get_dashboard_settings()

    threshold = settings["moisture_threshold"]
    automatic_watering = settings["automatic_watering_enabled"]

    if average_moisture < threshold and automatic_watering:
        return True

    return False


def trigger_automatic_watering(average_moisture):
    global last_automatic_watering_time

    settings = get_dashboard_settings()

    current_time = time.monotonic()

    if not check_watering_condition(average_moisture):
        return False

    if current_time - last_automatic_watering_time < 60:
        return False

    duration = settings["watering_duration"]
    manual_watering(duration)

    last_automatic_watering_time = current_time

    return True

def monitoring_cycle():
    global last_logged_time

    moisture = get_moisture_reading()
    settings = get_dashboard_settings()
    threshold = settings["moisture_threshold"]

    if moisture < threshold:
        average_moisture = confirm_low_moisture(moisture)
        trigger_automatic_watering(average_moisture)
        last_logged_time = time.monotonic()
    else:
        current_time = time.monotonic()
        if current_time - last_logged_time >= config.LOGGING_INTERVAL_SECONDS:
            save_moisture_reading(moisture)
            last_logged_time = current_time
            

def monitoring_loop():
    while True:
        try:
            monitoring_cycle()
        except Exception as error:
            print(f"Monitoring error: {error}")

        time.sleep(config.MONITORING_INTERVAL_SECONDS)


def start_monitoring():
    monitoring_thread = threading.Thread(
        target=monitoring_loop,
        daemon=True
    )

    monitoring_thread.start()

