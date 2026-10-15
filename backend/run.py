# THIS IS THE ENTRY POINT AND UH... yeah
import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG") == "1"
    app.run(host=os.getenv("HOST", "127.0.0.1"), port = 5000, debug=debug)
    