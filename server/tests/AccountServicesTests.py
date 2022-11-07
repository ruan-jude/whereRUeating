import unittest
# from unittest.mock import mock
import sys
from unittest import mock
import constants
import mariadb

sys.path.insert(1, constants.PATH_TO_MODULES)
print(sys.path)

from AccountServices import *
from DatabaseServices import setup_cursor

class TestAccountServices(unittest.TestCase):
    
    def test_verify_password(self):
        self.assertEqual(authenticate_account("doesnotexist", "passwordorsomething"), "Invalid login: user does not exist", "User should not exist")
        
    def test_verify_password_correct_login(self):
        self.assertEqual(authenticate_account("testUser", "testpassword"), "Valid login", "Login should be valid")

    def test_verify_password_wrong_password(self):
        self.assertEqual(authenticate_account("testUser", "password"), "Incorrect login", "Password should be wrong")

    def test_create_account_user_already_exists(self):
        self.assertEqual(create_account("testemail@gmail.com", "testUser", "somepassword", "somepassword"), "Account with that email already exists!", "Email should be used for account already")

    def test_create_account_password_match(self):
        self.assertEqual(create_account("newEmail@gmail.com", "some_username", "password", "does_not_match"), "Passwords do not match!", "Passwords should not match")

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_create_account_successfully(self, mock):
        create_account("newemail100@gmail.com", "some_username", "password1", "password1")
        mock.assert_called()

    def test_add_user_preference_error(self):
        self.assertEqual(add_user_preference("testUserNot", ["asdf", "asdfasd", "asddsfdds"]), "ERROR: User does not exist")

    # does not work. still figuring out how this mock/stub works
    # base_query = "INSERT INTO userPreferences (user_id, tag_name) VALUES (?, ?)"
    # @mock.patch.object(mariadb.Cursor, "execute")
    # def test_add_user_preference_success(self, mock):    
    #     add_user_preference("testUser", ("asdf", "asdfasd", "asddsfdds"))
    #     mock.assert_called()

if __name__ == '__main__':
    unittest.main()