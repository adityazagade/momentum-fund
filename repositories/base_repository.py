import psycopg2

from config.app_config import AppConfig


class BaseRepository:
    def __init__(self):
        app_config = AppConfig('app.properties')

        db_params = {
            "dbname": app_config.get('database.name'),
            "user": app_config.get('database.username'),
            "password": app_config.get('database.password'),
            "host": app_config.get('database.host'),
            "port": app_config.get('database.port')
        }
        self.conn = psycopg2.connect(**db_params)
