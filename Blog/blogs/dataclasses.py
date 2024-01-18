import configparser
from dataclasses import dataclass

@dataclass
class Settings:
    '''
    This dataclass to store azure chatgpt configuration.
    '''
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('blogs/settings.ini')
        self.secret_key = self.config['chatgpt']['secret_key']
        self.url = self.config['chatgpt']['url']