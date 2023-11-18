import psycopg2

from services.config_service import ConfigService


class BaseRepository:
    def __init__(self):
        config_service = ConfigService.get_instance()

        db_params = {
            "dbname": config_service.get('database.name'),
            "user": config_service.get('database.username'),
            "password": config_service.get('database.password'),
            "host": config_service.get('database.host'),
            "port": config_service.get('database.port')
        }
        self.conn = psycopg2.connect(**db_params)
