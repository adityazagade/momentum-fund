from flask import Flask
from flask_cors import CORS

from config.app_config import AppConfig
from controller.webhook_controller import create_webhook_routes

if __name__ == '__main__':
    app_config = AppConfig("app.properties")
    debug = app_config.get('app.debug')
    host = app_config.get('app.host')
    port = app_config.get('app.port')

    app = Flask(__name__)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    create_webhook_routes(app)
    app.run(debug=debug, port=port, host=host)
