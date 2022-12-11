import unittest
import sys
from unittest import mock
if __name__ == '__main__':
    import constants
else:    
    import test.constants as constants

sys.path.insert(1, constants.PATH_TO_PROJECT)

from server.DatabaseServices import *
from server.HelperMethods import *

class TestHelperMethods(unittest.TestCase):
    
    def test_synthesize_whitelist(self):
            test_list = ["asdf", "asdf"]
            test_list1 = ["asdf", "asdf"]
            result = test_list + test_list1
            self.assertEqual(synthesizeWhitelist(test_list, test_list1), result, "Lists should be identical")

    def test_isolate_tag_names(self):
        raw_whitelist = [("asdf", ), ("jerma", "983")]
        raw_blacklist = [("jerma985",), ("some tag name",)]
        expected_whitelist = ["asdf", "jerma"] 
        expected_blacklist = ["jerma985", "some tag name"]
        self.assertEqual(isolateTagNames(raw_whitelist, raw_blacklist), (expected_whitelist, expected_blacklist))

    def test_isolate_first_value_from_tuple(self):
        lorum = [("lorum", "sit"), ("ipsum", "amet"), ("dolor", "fi")]
        expected_set = ["lorum", "ipsum", "dolor"]
        test_return = isolateFirstValueFromTuple(lorum)
        self.assertEqual(test_return, expected_set)

    def test_isolate_first_value_from_singleton_tuple(self):
        lorum = [("lorum",), ("ipsum",), ("dolor",)]
        expected_set = ["lorum", "ipsum", "dolor"]
        test_return = isolateFirstValueFromTuple(lorum)
        self.assertEqual(test_return, expected_set)

if __name__ == '__main__':
    unittest.main()