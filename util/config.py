#!/usr/bin/python3
"""
Config module
Reads configuration file
"""
import os.path
import yaml

class Config():
    """The Config class loads the config YAML file"""

    def __init__(self, config_path=None):
        self.config = dict()

        if config_path:
            with open(config_path) as file:
                self.config = yaml.load(file)
        else:
            try:
                with open('config.yml') as file:
                    self.config = yaml.load(file)
            except OSError:
                with open('config.default.yml') as file:
                    self.config = yaml.load(file)

    def get_config(self):
        """Fetch basic configs"""
        return self.config

    def get_mail_config(self):
        """Fetch mail configs"""
        return self.config["mail"]

    def get_database_path(self):
        """Fetch database path from config"""
        path = self.config["database"]["path"]
        if not os.path.isfile(path):
            msg = "sqlite database %s does not exist, check the config(.default).json!" % path
            raise Exception(msg)
        return path

    def get_co2_avoidance_factor(self):
        """Fetch CO2 avoidance factor from config"""
        return self.config["co2_avoidance_factor"]

    def get_renamings(self):
        """Fetch inverter's name from config"""
        return self.config["renaming"]

    @staticmethod
    def log(msg, error=''):
        """Define logging"""
        if error:
            print(' *', msg, '['+str(error)+']')
        else:
            print(' *', msg)


if __name__ == '__main__':

    CFG = Config(config_path='../config.yml')
    print(CFG.get_config())
    print(CFG.get_co2_avoidance_factor())
