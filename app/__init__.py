from flask import Flask
from app.routes import main

def create_app():
    app = Flask(__name__, static_folder='../static')
    app.register_blueprint(main)
    return app
