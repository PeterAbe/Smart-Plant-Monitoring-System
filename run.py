from app import app
from database.db import db_init
from services.monitoring import start_monitoring


if __name__ == "__main__":
    db_init()
    start_monitoring()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
