from flask import Flask
from flask_cors import CORS
from controller.webhook_controller import create_webhook_routes

if __name__ == '__main__':
    app = Flask(__name__)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    create_webhook_routes(app)
    app.run(debug=True, port=7999, host='localhost')
