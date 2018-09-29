#!/usr/bin/python3
"""
"""
import json, os.path
from datetime import datetime

class Config():

    def __init__(self, config_path=None):
        self.config = dict()

        if config_path:
            with open(config_path) as f:
                self.config = json.load(f)
        else:
            try:
                with open('config.json') as f:
                    self.config = json.load(f)
            except:
                with open('config.default.json') as f:
                    self.config = json.load(f)

    def get_config(self):
        return self.config

    def get_mail_config(self):
        return self.config["mail"]

    def get_database_path(self):
        path = self.config["database"]["path"]
        if os.path.isfile(path):
            return self.config["database"]["path"]
        else:
            raise Exception("sqlite database %s does not exist, check the config(.default).json!" % path)

    def get_co2_avoidance_factor(self):
        return self.config["co2_avoidance_factor"]

    def log(self, msg, error=''):
        ts = datetime.now()
        if error: print(' *', msg, '['+str(error)+']')
        else: print(' *', msg)