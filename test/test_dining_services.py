import unittest
import sys
from unittest import mock
from unittest.mock import patch
if __name__ == '__main__':
    import constants
else:    
    import test.constants as constants

sys.path.insert(1, constants.PATH_TO_PROJECT)

from server.DiningServices import *
from datetime import datetime

def mocked_now(hour, minute):
    return datetime(2022, 1, 1, hour, minute, 0)

class TestDiningServices(unittest.TestCase):    

    @mock.patch('datetime.datetime', wraps=datetime)
    def test_check_dining_halls_busy_11_40(self, mock):
        mock.now.return_value = mocked_now(11, 40)
        return_message = "Classes just ended at 11:40 AM, so the dining halls might get/be busy now."
        self.assertEqual(check_dining_halls_busy(), return_message)

    @mock.patch('datetime.datetime', wraps=datetime)
    def test_check_dining_halls_busy_13_20(self, mock):
        mock.now.return_value = mocked_now(13, 20)
        return_message = "Classes just ended at 01:20 PM, so the dining halls might get/be busy now."
        self.assertEqual(check_dining_halls_busy(), return_message)

    @mock.patch('datetime.datetime', wraps=datetime)
    def test_check_dining_halls_busy_15_20(self, mock):
        mock.now.return_value = mocked_now(15, 20)
        return_message = "Classes just ended at 03:20 PM, so the dining halls might get/be busy now."
        self.assertEqual(check_dining_halls_busy(), return_message)

    @mock.patch('datetime.datetime', wraps=datetime)
    def test_check_dining_halls_busy_18_00(self, mock):
        mock.now.return_value = mocked_now(18, 0)
        return_message = "Classes just ended at 06:00 PM, so the dining halls might get/be busy now."
        self.assertEqual(check_dining_halls_busy(), return_message)

    @mock.patch('datetime.datetime', wraps=datetime)
    def test_check_dining_halls_busy_10_00(self, mock):
        mock.now.return_value = mocked_now(10, 0)
        return_message = "Probably not busy at this time."
        self.assertEqual(check_dining_halls_busy(), return_message)

    @mock.patch('datetime.datetime', wraps=datetime)
    def test_check_dining_halls_busy_14_20(self, mock):
        mock.now.return_value = mocked_now(14, 20)
        return_message = "Probably not busy at this time."
        self.assertEqual(check_dining_halls_busy(), return_message)

    @mock.patch('datetime.datetime', wraps=datetime)
    def test_check_dining_halls_busy_19_00(self, mock):
        mock.now.return_value = mocked_now(19, 00)
        return_message = "Probably not busy at this time."
        self.assertEqual(check_dining_halls_busy(), return_message)

if __name__ == '__main__':
    unittest.main()