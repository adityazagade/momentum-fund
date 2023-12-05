from flask import jsonify, request
from config.app_config import AppConfig
from services.strategy_executor import StrategyExecutor
from services.portfolio_service import PortfolioService
from services.ticker_historical_data import TickerDataService


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


def init():
    # read the cash_flow query param and pass it to the strategy executor
    cash_flow_query_param = request.args.get('cash_flow')
    if cash_flow_query_param is not None:
        cash_flow = float(cash_flow_query_param)
    else:
        cash_flow = 0.0
    executor = StrategyExecutor()
    result = executor.execute(cash_flow=cash_flow)
    message = 'Strategy executed successfully'
    return jsonify(success=True, message=message, data=result)


def get_portfolio():
    portfolio_service = PortfolioService()
    portfolio = portfolio_service.get_portfolio()
    ticker_service = TickerDataService()
    last_close_prices = ticker_service.get_current_prices(portfolio.get_tickers())
    return jsonify(success=True, data=portfolio.to_dict(last_close_prices))


def create_webhook_routes(app):
    app.route('/api/test', methods=['GET'])(get_endpoint)
    app.route('/api/init', methods=['GET'])(init)
    app.route('/api/webhook', methods=['POST'])(post_endpoint)
    app.route('/api/portfolio', methods=['GET'])(get_portfolio)
