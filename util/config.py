#!/usr/bin/python3
"""
Config module
Reads configuration file
"""
import yaml
import os.path

class Config():
    """The Config class loads the config YAML file"""

    def __init__(self, config_path=None):
        self.config = dict()

        if config_path:
            with open(config_path) as f:
                self.config = yaml.load(f)
        else:
            try:
                with open('config.yml') as f:
                    self.config = yaml.load(f)
            except Exception:
                with open('config.default.yml') as f:
                    self.config = yaml.load(f)

    def get_config(self):
        return self.config

    def get_mail_config(self):
        return self.config["mail"]

    def get_database_path(self):
        path = self.config["database"]["path"]
        if os.path.isfile(path):
            return self.config["database"]["path"]
        else:
            msg = "sqlite database %s does not exist, check the config(.default).json!" % path
            raise Exception(msg)

    def get_co2_avoidance_factor(self):
        return self.config["co2_avoidance_factor"]

    def get_renamings(self):
        return self.config["renaming"]

    def log(self, msg, error=''):
        if error: print(' *', msg, '['+str(error)+']')
        else: print(' *', msg)


if __name__ == '__main__':

    cfg = Config(config_path='../config.yml')
    print(cfg.get_config())
    print(cfg.get_co2_avoidance_factor())
