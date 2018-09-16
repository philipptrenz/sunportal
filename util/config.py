#!/usr/bin/python3
"""
"""
import json

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
        return self.config["database"]["path"]

    def get_co2_avoidance_factor(self):
        return self.config["co2_avoidance_factor"]