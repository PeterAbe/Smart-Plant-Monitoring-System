import time
import threading
import config

from hardware.water_pump import pump_on, pump_off
from database.models import add_watering_event, get_latest_reading


def _thread_function(duration, triggered_by, moisture_before):
    try:
        pump_on()
        time.sleep(duration)
    finally:
        pump_off()

    if moisture_before is not None:
        add_watering_event(
            duration=duration,
            triggered_by=triggered_by,
            moisture_before=moisture_before
        )
    else:
        print(
            "Watering completed, but the event could not be logged "
            "because no moisture reading was available."
        )


def manual_watering(duration, triggered_by="manual", moisture_before=None):
    # Validate watering duration
    if isinstance(duration, bool) or not isinstance(duration, int):
        raise ValueError("Watering duration must be an integer.")

    if not (
        config.MIN_WATERING_DURATION_SECONDS
        <= duration
        <= config.MAX_WATERING_DURATION_SECONDS
    ):
        raise ValueError("Watering duration is out of range.")

    # Validate watering trigger
    if triggered_by not in ("manual", "automatic"):
        raise ValueError("Invalid watering trigger.")

    # Get the latest moisture reading if one wasn't provided
    if moisture_before is None:
        latest_reading = get_latest_reading()
        if latest_reading is not None:
            moisture_before = latest_reading["moisture"]

    # Start watering in a separate thread
    watering_thread = threading.Thread(
        target=_thread_function,
        args=(duration, triggered_by, moisture_before),
        daemon=True
    )
    watering_thread.start()

    return 1
