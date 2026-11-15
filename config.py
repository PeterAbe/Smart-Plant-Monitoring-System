# configuration file for the application
# Every module imports its settings from here, values live in one place, and can be changed easily
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "smart_plant.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
# for testing purposes, so we always have a fresh database, we can use an in-memory database for testing, so we don't have to worry about cleaning up the database after tests
TEST_DATABASE_PATH = ":memory:"

# some default values for the application
DEFAULT_PLANT_NAME = "My Plant"
# default watering duration in seconds, idk how long we can change default after testing
DEFAULT_WATERING_DURATION_SECONDS = 5
# moisture threshold (%) for watering, if the moisture level is below this value, we water the plant
DEFAULT_MOISTURE_THRESHOLD = 30
# allow user to set if they want to allow automatic watering or not, default is True
DEFAULT_ALLOW_AUTOMATIC_WATERING = True
# Default temperature units, can be "C" for Celsius or "F" for Fahrenheit, default is "C"
DEFAULT_TEMPERATURE_UNITS = "C"

# Threshhold for moisture, humidity, and temperature, if the values are outside of these ranges, we raise a warning for plant comfort, these values are used to determine if the plant is in a comfortable environment or not.
# percentage of moisture, 0-100%, if the moisture is not within this range, we raise a warning for plant comfort
MIN_MOISTURE = 0
MAX_MOISTURE = 100
# percentage of humidity, 0-100%, if the humidity is not within this range, we raise a warning for plant comfort
MIN_HUMIDITY = 0
MAX_HUMIDITY = 100
# temperature in Celsius, if the temperature is not within this range, we raise a warning for plant comfort
MIN_TEMPERATURE = -40
MAX_TEMPERATURE = 85

#logging interval in seconds, how often we log the moisture level to the database, can change to 1 seconds for testing purposes, but default is 60 seconds
LOGGING_INTERVAL_SECONDS = 60