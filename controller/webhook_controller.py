from flask import jsonify, request

from config.app_config import AppConfig
from services.portfolio_service import PortfolioService


def update_request_token(request_token):
    app_config = AppConfig('app.properties')
    app_config.set('kite.request_token', request_token)
    app_config.write()


def get_endpoint():
    return jsonify(success=True)


def post_endpoint():
    # update request token in app.properties
    request_token = request.args.get('request_token')
    update_request_token(request_token)
    return jsonify(success=True)


def init_rebalance():
    portfolio_service = PortfolioService()
    portfolio_service.init_rebalance()
    return jsonify(success=True)


def create_webhook_routes(app):
    app.route('/api/test', methods=['GET'])(get_endpoint)
    app.route('/api/init', methods=['GET'])(init_rebalance)
    app.route('/api/webhook', methods=['POST'])(post_endpoint)
