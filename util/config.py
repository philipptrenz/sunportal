#!/usr/bin/python3
"""
"""
import json, os.path

class Config():

    def __init__(self):
        self.config = dict()
        try:
            with open('config.json') as f:
                self.config = json.load(f)
        except:
            with open('config.default.json') as f:
                self.config = json.load(f)

    def get_config(self):
        return self.config

    def get_database_path(self):
        path = self.config["database"]["path"]
        if os.path.isfile(path):
            return self.config["database"]["path"]
        else:
            raise Exception("sqlite database %s does not exist, check the config(.default).json!" % path)

    def get_co2_avoidance_factor(self):
        return self.config["co2_avoidance_factor"]