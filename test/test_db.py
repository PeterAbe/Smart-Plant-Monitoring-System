# Tests for the database module
# Run from repo root:
#   python -m pytest test/test_db.py -v
import pytest
import config
from database.db import db_connect, db_init
from datetime import date, datetime, timedelta, timezone
from database.models import add_sensor_reading, get_latest_reading, get_readings, get_readings_for_day


# Fixture: a fresh, empty IN-MEMORY database for every test
@pytest.fixture
def db_connection():
    # FIX: use the test DB, not the real file
    conn = db_connect(config.TEST_DATABASE_PATH)
    # FIX: pass the connection in - :memory: tables only exist on this connection
    db_init(conn)
    yield conn
    conn.close()

def test_add_sensor_reading_valid(db_connection):
    # Test adding a valid sensor reading
    reading_id = add_sensor_reading(moisture=50, temperature=25, humidity=60,
                                    extra_text={"location": "greenhouse"},
                                    timestamp="2026-11-14T13:00:00+00:00",
                                    conn=db_connection)
    assert isinstance(reading_id, int)

def test_add_sensor_reading_invalid_moisture(db_connection):
    # Test adding a sensor reading with invalid moisture value
    with pytest.raises(ValueError):
        add_sensor_reading(moisture=150, temperature=25, humidity=60,
                           extra_text={"location": "greenhouse"},
                           timestamp="2026-11-14T13:00:00+00:00",
                           conn=db_connection)

def test_invalid_reading_is_not_saved(db_connection):
    # Test that an invalid reading is not saved to the database
    with pytest.raises(ValueError):
        add_sensor_reading(moisture=150, conn=db_connection)
    assert get_latest_reading(conn=db_connection) is None

def test_get_latest_reading(db_connection):
    # Test retrieving the latest sensor reading
    add_sensor_reading(moisture=50, temperature=25, humidity=60,
                       extra_text={"location": "greenhouse"},
                       timestamp="2026-11-14T13:00:00+00:00",
                       conn=db_connection)
    latest_reading = get_latest_reading(conn=db_connection)
    assert latest_reading is not None
    assert latest_reading['moisture'] == 50
    assert latest_reading['temperature'] == 25
    assert latest_reading['humidity'] == 60
    assert latest_reading['extra_text'] == {"location": "greenhouse"}

def test_get_latest_reading_no_data(db_connection):
    # Test retrieving the latest sensor reading when no data is present
    latest_reading = get_latest_reading(conn=db_connection)
    assert latest_reading is None

def test_add_sensor_reading_invalid_temperature(db_connection):
    # Test adding a sensor reading with invalid temperature value
    with pytest.raises(ValueError):
        add_sensor_reading(moisture=50, temperature=150, humidity=60,
                           extra_text={"location": "greenhouse"},
                           timestamp="2026-11-14T13:00:00+00:00",
                           conn=db_connection)

def test_add_sensor_reading_invalid_humidity(db_connection):
    # Test adding a sensor reading with invalid humidity value
    with pytest.raises(ValueError):
        add_sensor_reading(moisture=50, temperature=25, humidity=150,
                           extra_text={"location": "greenhouse"},
                           timestamp="2026-11-14T13:00:00+00:00",
                           conn=db_connection)

def test_add_sensor_reading_invalid_extra_text(db_connection):
    # Test adding a sensor reading with extra_text that is not a dictionary
    with pytest.raises(ValueError):
        add_sensor_reading(moisture=50, temperature=25, humidity=60,
                           extra_text="not a dict",
                           timestamp="2026-11-14T13:00:00+00:00",
                           conn=db_connection)

def test_add_sensor_reading_missing_moisture(db_connection):
    # Test adding a sensor reading with missing moisture value
    with pytest.raises(ValueError):
        add_sensor_reading(moisture=None, temperature=25, humidity=60,
                           extra_text={"location": "greenhouse"},
                           timestamp="2026-11-14T13:00:00+00:00",
                           conn=db_connection)

def test_add_sensor_reading_default_values(db_connection):
    # Test adding a sensor reading with default values for optional parameters
    reading_id = add_sensor_reading(moisture=50, conn=db_connection)
    assert isinstance(reading_id, int)
    latest_reading = get_latest_reading(conn=db_connection)
    assert latest_reading['moisture'] == 50
    assert latest_reading['temperature'] is None
    assert latest_reading['humidity'] is None
    assert latest_reading['extra_text'] is None

def test_add_sensor_reading_timestamp_none(db_connection):
    # Test adding a sensor reading with timestamp set to None (should use current time)
    reading_id = add_sensor_reading(moisture=50, timestamp=None, conn=db_connection)
    assert isinstance(reading_id, int)
    latest_reading = get_latest_reading(conn=db_connection)
    assert latest_reading['moisture'] == 50
    assert latest_reading['timestamp'] is not None

# NOTE: this FAILS until add_sensor_reading validates timestamps
def test_add_sensor_reading_invalid_timestamp(db_connection):
    # Test adding a sensor reading with an invalid timestamp format
    with pytest.raises(ValueError):
        add_sensor_reading(moisture=50, timestamp="invalid-timestamp", conn=db_connection)

def test_add_sensor_reading_edge_case_values(db_connection):
    # Test that the exact min/max values from config are allowed (catches < vs <= bugs)
    reading_id = add_sensor_reading(moisture=config.MIN_MOISTURE, temperature=config.MIN_TEMPERATURE,
                                    humidity=config.MIN_HUMIDITY,
                                    timestamp="2026-11-14T12:00:00+00:00",
                                    conn=db_connection)
    assert isinstance(reading_id, int)
    latest_reading = get_latest_reading(conn=db_connection)
    assert latest_reading['moisture'] == config.MIN_MOISTURE
    assert latest_reading['temperature'] == config.MIN_TEMPERATURE
    assert latest_reading['humidity'] == config.MIN_HUMIDITY

    reading_id = add_sensor_reading(moisture=config.MAX_MOISTURE, temperature=config.MAX_TEMPERATURE,
                                    humidity=config.MAX_HUMIDITY,
                                    timestamp="2026-11-14T13:00:00+00:00",
                                    conn=db_connection)
    assert isinstance(reading_id, int)
    latest_reading = get_latest_reading(conn=db_connection)
    assert latest_reading['moisture'] == config.MAX_MOISTURE
    assert latest_reading['temperature'] == config.MAX_TEMPERATURE
    assert latest_reading['humidity'] == config.MAX_HUMIDITY

def test_add_sensor_reading_multiple_entries(db_connection):
    # Test adding multiple sensor readings and retrieving the latest one
    add_sensor_reading(moisture=30, temperature=20, humidity=50,
                       extra_text={"location": "greenhouse1"},
                       timestamp="2026-11-14T12:00:00+00:00",
                       conn=db_connection)
    add_sensor_reading(moisture=40, temperature=22, humidity=55,
                       extra_text={"location": "greenhouse2"},
                       timestamp="2026-11-14T13:00:00+00:00",
                       conn=db_connection)
    latest_reading = get_latest_reading(conn=db_connection)
    assert latest_reading['moisture'] == 40
    assert latest_reading['temperature'] == 22
    assert latest_reading['humidity'] == 55
    # FIX: dict, not JSON string
    assert latest_reading['extra_text'] == {"location": "greenhouse2"}

def test_latest_uses_timestamp_not_insert_order(db_connection):
    # Test that the latest reading is determined by timestamp, not insertion order
    add_sensor_reading(moisture=40, timestamp="2026-11-14T13:00:00+00:00", conn=db_connection)
    add_sensor_reading(moisture=30, timestamp="2026-11-14T12:00:00+00:00", conn=db_connection)
    latest_reading = get_latest_reading(conn=db_connection)
    assert latest_reading['moisture'] == 40

def test_db_init_is_safe_to_run_twice(db_connection):
    # Test that db_init can be run multiple times without error
    db_init(db_connection)
    count = db_connection.execute("SELECT COUNT(*) FROM dashboard_settings").fetchone()[0]
    assert count == 1

def _add_three_readings(conn):
    # Helper: readings at 12:00, 13:00, 14:00 UTC, inserted OUT of order
    add_sensor_reading(moisture=50, timestamp="2026-11-14T13:00:00+00:00", conn=conn)
    add_sensor_reading(moisture=60, timestamp="2026-11-14T14:00:00+00:00", conn=conn)
    add_sensor_reading(moisture=40, timestamp="2026-11-14T12:00:00+00:00", conn=conn)


def test_get_readings_empty_db_returns_empty_list(db_connection):
    # Test that get readings returns empty list
    assert get_readings(conn=db_connection) == []


def test_get_readings_start_included_end_excluded(db_connection):
    # Test that has in range
    _add_three_readings(db_connection)
    readings = get_readings(start_time="2026-11-14T12:00:00+00:00",
                            end_time="2026-11-14T14:00:00+00:00",
                            conn=db_connection)
    assert [r['moisture'] for r in readings] == [40, 50]


def test_get_readings_sorted_oldest_first(db_connection):
    # Test getting readings from oldest first
    _add_three_readings(db_connection)
    readings = get_readings(conn=db_connection)
    timestamps = [r['timestamp'] for r in readings]
    assert timestamps == sorted(timestamps)


def test_get_readings_no_range_returns_all(db_connection):
    _add_three_readings(db_connection)
    assert len(get_readings(conn=db_connection)) == 3


def test_get_readings_only_start(db_connection):
    _add_three_readings(db_connection)
    readings = get_readings(start_time="2026-11-14T13:00:00+00:00", conn=db_connection)
    assert [r['moisture'] for r in readings] == [50, 60]


def test_get_readings_only_end(db_connection):
    _add_three_readings(db_connection)
    readings = get_readings(end_time="2026-11-14T13:00:00+00:00", conn=db_connection)
    assert [r['moisture'] for r in readings] == [40]


def test_get_readings_limit(db_connection):
    _add_three_readings(db_connection)
    readings = get_readings(limit=2, conn=db_connection)
    # Oldest two
    assert [r['moisture'] for r in readings] == [40, 50]


@pytest.mark.parametrize("bad_limit", [0, -1, "10", True, 2.5])
def test_get_readings_invalid_limit_raises(db_connection, bad_limit):
    with pytest.raises(ValueError):
        get_readings(limit=bad_limit, conn=db_connection)


def test_get_readings_start_after_end_raises(db_connection):
    with pytest.raises(ValueError):
        get_readings(start_time="2026-11-14T14:00:00+00:00",
                     end_time="2026-11-14T12:00:00+00:00",
                     conn=db_connection)


def test_get_readings_invalid_start_raises(db_connection):
    with pytest.raises(ValueError):
        get_readings(start_time="not-a-date", conn=db_connection)


def test_get_readings_decodes_extra_text(db_connection):
    add_sensor_reading(moisture=50, extra_text={"location": "greenhouse"},
                       timestamp="2026-11-14T13:00:00+00:00", conn=db_connection)
    readings = get_readings(conn=db_connection)
    assert readings[0]['extra_text'] == {"location": "greenhouse"}


def test_get_readings_handles_timezone_offset(db_connection):
    _add_three_readings(db_connection)
    readings = get_readings(start_time="2026-11-14T08:00:00-05:00", conn=db_connection)
    assert [r['moisture'] for r in readings] == [50, 60]


def test_add_sensor_reading_normalizes_timezone(db_connection):
    add_sensor_reading(moisture=50, timestamp="2026-11-14T08:00:00-05:00", conn=db_connection)
    assert get_latest_reading(conn=db_connection)['timestamp'] == "2026-11-14T13:00:00+00:00"

TEST_TZ = timezone(timedelta(hours=-5))


def _add_readings_around_nov_14(conn):
    # Timestamps are in UTC-5 local time
    add_sensor_reading(moisture=10, timestamp="2026-11-13T23:59:00-05:00", conn=conn)  # day before
    add_sensor_reading(moisture=20, timestamp="2026-11-14T00:00:00-05:00", conn=conn)  # start of day
    add_sensor_reading(moisture=30, timestamp="2026-11-14T12:00:00-05:00", conn=conn)  # noon
    add_sensor_reading(moisture=40, timestamp="2026-11-14T23:59:00-05:00", conn=conn)  # end of day
    add_sensor_reading(moisture=50, timestamp="2026-11-15T00:00:00-05:00", conn=conn)  # next day


def test_get_readings_for_day_only_that_day(db_connection):
    _add_readings_around_nov_14(db_connection)
    readings = get_readings_for_day("2026-11-14", timezone=TEST_TZ, conn=db_connection)
    # Start midnight included, next midnight excluded
    assert [r['moisture'] for r in readings] == [20, 30, 40]


def test_get_readings_for_day_empty_day(db_connection):
    _add_readings_around_nov_14(db_connection)
    assert get_readings_for_day("2026-11-20", timezone=TEST_TZ, conn=db_connection) == []


def test_get_readings_for_day_accepts_date_object(db_connection):
    _add_readings_around_nov_14(db_connection)
    from_string = get_readings_for_day("2026-11-14", timezone=TEST_TZ, conn=db_connection)
    from_date = get_readings_for_day(date(2026, 11, 14), timezone=TEST_TZ, conn=db_connection)
    assert from_string == from_date


@pytest.mark.parametrize("bad_day", ["14/11/2026", "not-a-date", "2026-13-01", 12345])
def test_get_readings_for_day_invalid_day_raises(db_connection, bad_day):
    with pytest.raises(ValueError):
        get_readings_for_day(bad_day, timezone=TEST_TZ, conn=db_connection)


def test_get_readings_for_day_rejects_datetime(db_connection):
    with pytest.raises(ValueError):
        get_readings_for_day(datetime.now(TEST_TZ), timezone=TEST_TZ, conn=db_connection)


def test_get_readings_for_day_defaults_to_today(db_connection):
    now = datetime.now(TEST_TZ)
    add_sensor_reading(moisture=60, timestamp=now, conn=db_connection)
    add_sensor_reading(moisture=70, timestamp=now - timedelta(days=2), conn=db_connection)
    readings = get_readings_for_day(timezone=TEST_TZ, conn=db_connection)
    assert [r['moisture'] for r in readings] == [60]


def test_get_readings_for_day_returns_full_day(db_connection):
    # One reading per minute for a whole day = 1440 readings.
    # Catches a limit that's too small (e.g. 1000 would cut off at ~4:40pm).
    start = datetime(2026, 11, 14, tzinfo=TEST_TZ)
    for minute in range(24 * 60):
        add_sensor_reading(moisture=50, timestamp=start + timedelta(minutes=minute),
                           conn=db_connection)
    readings = get_readings_for_day("2026-11-14", timezone=TEST_TZ, conn=db_connection)
    assert len(readings) == 24 * 60