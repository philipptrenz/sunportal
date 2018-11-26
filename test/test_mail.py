#!/usr/bin/python3
"""
Test class for sunportal's mail class
"""

import unittest
import sqlite3
from sqlite3 import OperationalError

from util.config import Config
from util.database import Database
from util.mail import Mail

class TestMail(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        c = self.conn.cursor()

        with open('sbfspot_sqlite_db_creation.sql', 'r') as sbfspot_sql_file:
            sql_statements =sbfspot_sql_file.read()
            sql_commands = sql_statements.split(';')

            for sql_command in sql_commands:
                try:
                    c.execute(sql_command)
                except OperationalError as error:
                    print("Command skipped:", error)

        self.conn.commit()

        self.insert_sample_data()


    def insert_sample_data(self):
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO Inverters ("Serial","Name","Type","SW_Version","TimeStamp","TotalPac","EToday","ETotal","OperatingTime","FeedInTime","Status","GridRelay","Temperature")
            VALUES (1234567890,"Sample Inverter","INV-001","s0-bridge v0","1538728800",NULL,3150,13695788,15725.0,15161.8,"OK","Closed",28.42);
        ''')

        c.execute('''
            INSERT INTO DayData ("TimeStamp","Serial","TotalYield","Power","PVoutput") 
            VALUES (1538728500,1234567890,34112325,1510,NULL);
        ''')

        c.execute('''
            INSERT INTO MonthData ("TimeStamp","Serial","TotalYield","DayYield")
            VALUES (1538694000,1234567890,34107530,11376);
        ''')

    def test_database_sample_data_insertion(self):
        c = self.conn.cursor()
        c.execute("SELECT * from Inverters")
        result = c.fetchall()
        print(result)

        c.execute("SELECT * from DayData")
        result = c.fetchall()
        print(result)

        c.execute("SELECT * from MonthData")
        result = c.fetchall()
        print(result)

    def tearDown(self):
        self.conn.close()

if __name__ == '__main__':
    unittest.main()