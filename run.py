from app import app
from services.monitoring import start_monitoring

if __name__ == "__main__":
    start_monitoring()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
