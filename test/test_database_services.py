import unittest
import sys
if __name__ == '__main__':
    import constants
else:    
    import test.constants as constants

sys.path.insert(1, constants.PATH_TO_PROJECT)
from server.DatabaseServices import *

class TestDatabaseServices(unittest.TestCase):

    def test_isolate_first_value_from_tuple(self):
        lorum = [("lorum", "sit"), ("ipsum", "amet"), ("dolor", "fi")]
        expected_set = ["lorum", "ipsum", "dolor"]
        test_return = isolate_first_value_from_tuple(lorum)
        self.assertEqual(test_return, expected_set)

    def test_isolate_first_value_from_singleton_tuple(self):
        lorum = [("lorum",), ("ipsum",), ("dolor",)]
        expected_set = ["lorum", "ipsum", "dolor"]
        test_return = isolate_first_value_from_tuple(lorum)
        self.assertEqual(test_return, expected_set)

if __name__ == '__main__':
    unittest.main()