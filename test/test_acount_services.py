import unittest
import sys
from unittest import mock
import test.constants as constants
import mariadb

sys.path.insert(1, constants.PATH_TO_PROJECT)

from server.AccountServices import *
from server.DatabaseServices import *

class TestAccountServices(unittest.TestCase):
    
    def test_verify_password_invalid_user(self):
        self.assertEqual(authenticate_account("doesnotexist", "passwordorsomething"), (False, "User does not exist"), "User should not exist")
        
    @unittest.skip("fix db query mismatch")
    def test_verify_password_correct_login(self):
        self.assertEqual(authenticate_account("testUser", "testpassword"), (True, "Valid login"), "Login should be valid")

    def test_verify_password_wrong_password(self):
        self.assertEqual(authenticate_account("testUser", "password"), (False, "Incorrect login"), "Password should be wrong")

    def test_create_account_user_already_exists(self):
        self.assertEqual(create_account("testemail@gmail.com", "testUser", "somepassword", "somepassword"), (False, "Account with that email already exists!"), "Email should be used for account already")

    def test_create_account_password_match(self):
        self.assertEqual(create_account("newEmail@gmail.com", "some_username", "password", "does_not_match"), (False, "Passwords do not match!"), "Passwords should not match")

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_create_account_successfully(self, mock):
        create_account("newemail100@gmail.com", "some_username", "password1", "password1")
        mock.assert_called()

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_add_user_preference_error(self, mock):
        whitelist = ["asdf", "asdfasd", "asddsfdds"]
        blacklist = ["lorum ipsum", "dolor sit"]
        combined = whitelist + blacklist
        self.assertEqual(add_user_preferences("testUserNot", whitelist, blacklist), None)
        self.assertEqual(mock.call_count, len(combined))

    def test_sanitize_info_success(self):
        #sanitize_info(email_input, username_input, password_input)
        self.assertEqual(sanitize_info("cameronhoang@rutgers.edu", "notCameron", "asdfasdfasdf"), True)

    def test_sanitize_info_password_too_short(self):
        self.assertEqual(sanitize_info("cameronhoang@rutgers.edu", "testtesttest", "short"), (False, "Password cannot be less than 8 characters long" ))

    def test_sanitize_info_username_too_long(self):
        self.assertEqual(sanitize_info("jerma985@jerma.edu", "JJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ", "ASDFASDFASDF"), (False, "Username too long"))

    def test_sanitize_info_improper_email(self):
        self.assertEqual(sanitize_info('asdfasdfasdf', 'someusername', 'somepassword'), (False, 'Invalid email address!'))

    def test_sanitize_info_email_too_long(self):
        self.assertEqual(sanitize_info('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa@gmail.com', 'username', 'password'), (False, "Email too long"))
    #self.assertEqual(sanitize_info(), (False, ))

    def test_synthesize_whitelist(self):
        test_list = ["asdf", "asdf"]
        test_list1 = ["asdf", "asdf"]
        result = test_list + test_list1
        self.assertEqual(synthesize_whitelist(test_list, test_list1), result, "Lists should be identical")

    # @mock.patch.object(mariadb.Cursor, "execute")
    # @mock.patch.object(mariadb.Cursor, "fetchall")
    # def test_get_user_preference(self, mock):
    #     get_user_preferences(1)
    #     num_queries = 2
    #     self.assertEqual(mock.call_count, num_queries)

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_delete_user_preference(self, mock):
        some_id = 45
        self.assertEqual(delete_user_preference(some_id), (True, "Preferences cleared!"))
        mock.assert_called()

    def test_isolate_tag_names(self):
        raw_whitelist = [("asdf", ), ("jerma", "983")]
        raw_blacklist = [("jerma985",), ("some tag name",)]
        expected_whitelist = ["asdf", "jerma"] 
        expected_blacklist = ["jerma985", "some tag name"]
        self.assertEqual(isolate_tag_names(raw_whitelist, raw_blacklist), (expected_whitelist, expected_blacklist))

if __name__ == '__main__':
    unittest.main()