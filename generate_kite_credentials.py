from kiteconnect import KiteConnect

from config.app_config import AppConfig

app_config = AppConfig('app.properties')

api_key = app_config.get('kite.api_key')
api_secret = app_config.get('kite.api_secret')
request_token = app_config.get('kite.request_token')

kite = KiteConnect(api_key=api_key)
if request_token is None or request_token == '':
    url = kite.login_url()
    print(url)
