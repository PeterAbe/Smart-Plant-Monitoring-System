from database.db import db_connect
from database.models import update_dashboard_settings

conn = db_connect()

update_dashboard_settings(
    plant_name="My Plant",
    moisture_threshold=30,
    watering_duration=5,
    automatic_watering_enabled=True,
    temperature_unit="C",
    conn=conn
)

print("Default settings restored.")

conn.close()