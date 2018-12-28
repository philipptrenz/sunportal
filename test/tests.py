#!/usr/bin/python3
"""
Test class for sunportal
"""

import unittest

from util.database import Database

class TestDatabase(unittest.TestCase):

    def test_get_epoch_day(self):

        res = Database.get_epoch_day(None, '1994-04-04')
        self.assertEqual(res, (765417600, 765503999))


    def test_get_last_day_of_month_leap_year(self):

        res = Database.get_last_day_of_month(None, '2020-02-05')
        self.assertEqual(res, 29)

    def test_get_last_day_of_month_no_leap_year(self):

        res = Database.get_last_day_of_month(None, '2019-02-05')
        self.assertEqual(res, 28)

    def test_get_last_day_of_month_month_and_year_swapped(self):
        with self.assertRaises(ValueError):
            Database.get_last_day_of_month(None, '2019-13-01')

    def test_convert_local_ts_to_utc_on_local_timezone(self):
        """
        The database sunportal uses contains timestamps not in UTC timezone (as per definition), but
        instead in local timezone. convert_local_ts_to_utc converts those timestamps back to UTC for
        further processing and timezone independent front-ends.
        """

        import time
        ts_in_utc = int(time.time()) # unix timestamps are per definition always in utc

        timezone = Database.get_local_timezone(None)
        utc_offset = timezone.utcoffset(None).seconds
        ts_in_local_time = ts_in_utc + utc_offset

        res = Database.convert_local_ts_to_utc(None, ts_in_local_time, timezone)
        self.assertEqual(res, ts_in_utc)


if __name__ == '__main__':

    unittest.main()
