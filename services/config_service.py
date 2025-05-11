"""
This module is responsible for reading properties from app.properties file and cookies file
"""

import glob
import os
from typing import Any
import re

APP_PROPERTIES = 'app.properties'


class ConfigService:
    """
    This class is responsible for reading properties from app.properties file and
    returning the value for a given key
    """
    instance = None

    def __init__(self) -> None:
        """
        This is a singleton class. Use get_instance() method to get the instance
        """
        super().__init__()
        self.properties = {}
        self.load_properties()

    @classmethod
    def get_instance(cls) -> 'ConfigService':
        """
        This method returns the singleton instance
        :return: ConfigService instance
        """
        if cls.instance is None:
            cls.instance = ConfigService()
        return cls.instance

    def get(self, key) -> Any:
        """
        This method returns the value for a given key
        :param key: string key
        :return: value for the key
        """
        if key not in self.properties:
            return None
        return self.properties[key]

    def load_properties(self) -> None:
        """
        This method loads the properties from app.properties,cookies file
        :return: None
        """
        self.load_app_properties()
        self.load_kite_cookies()

    def load_kite_cookies(self):
        """
        This method loads the cookies from the latest cookie file
        :return: None
        """
        # get the latest cookie file from the directory and load the cookies. all cookie files are named as
        # cookie_1700318683017.txt where 1700318683017 is the timestamp. The latest file will have the latest timestamp.
        cookie_files = glob.glob(self.properties.get('cookie_file_path_pattern'))
        # glob_glob = glob.glob('/Users/adityazagade/Downloads/cookie_*.txt')

        # Sort files by timestamp
        sorted_files = sorted(cookie_files, key=self.extract_timestamp, reverse=True)

        # Select the most recent file
        cookie_file = sorted_files[0] if sorted_files else None

        # cookie_file = max(cookie_files, key=os.path.getctime)

        """
        Loads cookies from the most recent cookie file if available.
        """
        
        if cookie_file is not None:
            with open(cookie_file, 'r', encoding='utf-8') as text_file:
                for line in text_file:
                    line = line.strip()
                    # split the line by ',' and store the key value pairs in a dictionary
                    for key_value_pair in line.split(','):
                        if key_value_pair and '=' in key_value_pair:
                            key, value = key_value_pair.split('=', 1)
                            appended_key = 'kite.ui.' + key.strip()
                            self.properties[appended_key] = value.strip()

    def load_app_properties(self):
        """
        This method loads the properties from app.properties file
        :return: None
        """
        """
        Loads properties from the app.properties file.
        """
        
        properties_file = 'app.properties'
        with open(properties_file, 'r', encoding='utf-8') as text_file:
            for line in text_file:
                line = line.strip()
                if line and '=' in line:
                    key, value = line.split('=', 1)
                    """
                    Sets the value for a given key in the properties.
        
                    :param key: string key
                    :param value: value to set
                    :return: None
                    """
                    self.properties[key.strip()] = value.strip()

    def get_or_default(self, key, default) -> Any:
        """
        This method returns the value for a given key. If the key is not present, it returns the
        default value
        :param key: string key
        :param default: default-value
        :return: value for the key
        """
        if key not in self.properties:
            return default
        return self.properties[key]

    def set(self, key, value):
        """
        This method sets the value for a given key
        :param key: string key
        :param value: value
        :return: None
        """
        self.properties[key] = value

    def write(self):
        """
        This method writes the properties to app.properties file
        :return:
        """
        """
        Writes the current properties to the app.properties file.
        """
        
        with open(APP_PROPERTIES, 'w', encoding='utf-8') as text_file:
            for key, value in self.properties.items():
                text_file.write(f'{key}={value}\n')

    # Function to extract timestamp from filename
    @staticmethod
    def extract_timestamp(filename):
        """
        This method extracts the timestamp from the given file name
        :param filename: filename
        :return: timestamp
        """
        match = re.search(r'cookie_(\d+)\.txt', filename)
        return int(match.group(1)) if match else 0
