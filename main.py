from flask import Flask
from flask_cors import CORS

from services.config_service import ConfigService
from controller.webhook_controller import create_webhook_routes

if __name__ == '__main__':
    config_service = ConfigService.get_instance()
    debug = config_service.get('app.debug')
    host = config_service.get('app.host')
    port = config_service.get('app.port')

    app = Flask(__name__)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    create_webhook_routes(app)
    app.run(debug=debug, port=port, host=host)
