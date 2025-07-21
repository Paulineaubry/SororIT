from flask import Flask
from flask_app.routes import routes
from dotenv import load_dotenv

def create_app():
    load_dotenv()  # Charge .env
    app = Flask(__name__)
    app.register_blueprint(routes)
    return app
