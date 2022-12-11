import unittest
import sys
from unittest import mock
if __name__ == '__main__':
    import constants
else:    
    import test.constants as constants
import mariadb

sys.path.insert(1, constants.PATH_TO_PROJECT)

from server.AccountServices import *
from server.DatabaseServices import *

class TestAccountServices(unittest.TestCase):
    
    def test_verify_password_invalid_user(self):
        self.assertEqual(authenticateAccount("doesnotexist", "passwordorsomething"), (False, "User does not exist"), "User should not exist")
        
    def test_verify_password_correct_login(self):
        return_tuple = (9, "testUser", "testEmail@gmail.com", "$2b$12$5dB0d0To7Gt5VxRoPYxS4ui1fkrY9n1zbq29h75bQnC5JUp.u1heu")
        self.assertEqual(authenticateAccount("testUser", "testPassword"), (True, return_tuple), "Login should be valid")

    def test_verify_password_wrong_password(self):
        self.assertEqual(authenticateAccount("testUser", "password"), (False, "Incorrect login"), "Password should be wrong")

    def test_create_account_user_already_exists(self):
        self.assertEqual(createAccount("testemail@gmail.com", "testUser", "somepassword", "somepassword"), (False, "Account with that email already exists!"), "Email should be used for account already")

    def test_create_account_password_match(self):
        self.assertEqual(createAccount("newEmail@gmail.com", "some_username", "password", "does_not_match"), (False, "Passwords do not match!"), "Passwords should not match")

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_create_account_successfully(self, mock):
        createAccount("newemail100@gmail.com", "some_username", "password1", "password1")
        mock.assert_called()

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_add_user_preference_error(self, mock):
        whitelist = ["asdf", "asdfasd", "asddsfdds"]
        blacklist = ["lorum ipsum", "dolor sit"]
        combined = whitelist + blacklist
        self.assertEqual(addUserPreferences("testUserNot", whitelist, blacklist), None)
        self.assertEqual(mock.call_count, len(combined))

    def test_sanitize_info_success(self):
        self.assertEqual(sanitizeInfo("cameronhoang@rutgers.edu", "notCameron", "asdfasdfasdf"), True)

    def test_sanitize_info_password_too_short(self):
        self.assertEqual(sanitizeInfo("cameronhoang@rutgers.edu", "testtesttest", "short"), (False, "Password cannot be less than 8 characters long" ))

    def test_sanitize_info_username_too_long(self):
        self.assertEqual(sanitizeInfo("jerma985@jerma.edu", "JJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ", "ASDFASDFASDF"), (False, "Username too long"))

    def test_sanitize_info_improper_email(self):
        self.assertEqual(sanitizeInfo('asdfasdfasdf', 'someusername', 'somepassword'), (False, 'Invalid email address!'))

    def test_sanitize_info_email_too_long(self):
        self.assertEqual(sanitizeInfo('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa@gmail.com', 'username', 'password'), (False, "Email too long"))

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_clear_user_preferences(self, mock):
        some_id = 45
        # self.assertEqual(clearUserPreferences(some_id), (True, "Preferences cleared!"))
        clearUserPreferences(some_id)
        mock.assert_called_with("DELETE FROM userPreferences WHERE user_id = ?", (some_id, ))

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_get_user_preferences(self, mock):
        mock.return_value = (("asdf",),)
        expected_list = (["asdf"], ["asdf"])
        self.assertEqual(getUserPreferences(123), expected_list)

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_clear_user_favs(self, mock):
        expected_query = "DELETE FROM userFavs WHERE user_id=?"
        some_id = 123
        clearUserFavs(some_id)
        mock.assert_called_with(expected_query, (some_id,))

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_get_user_favs(self, mock):
        expected_list = [123, 123, 1222] 
        mock.return_value = ((123, ), (123, ), (1222, ))
        self.assertEqual(getUserFavs(123), expected_list)

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_add_user_favs(self, mock):
        test_dish_list = (123, 125, 126, 136)
        test_user_id = 11
        addUserFavs(test_user_id, test_dish_list)
        self.assertEqual(mock.call_count, len(test_dish_list))

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_get_all_users(self, mock):
        user_list = [(1, "some user"), (2, "jerma985"), (3, "peeped_horror")]
        mock.return_value = user_list
        self.assertEqual(getAllUsers(), user_list)

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_get_user_role_has_role(self, mock):
        role_list = [(1, )]
        mock.return_value = role_list
        self.assertEqual(getUserRole(12), role_list[0][0])


    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_get_user_role_has_no_roles(self, mock):
        role_list = None
        mock.return_value = role_list
        self.assertEqual(getUserRole(12), role_list)

        role_list = ()
        mock.return_value = role_list
        self.assertEqual(getUserRole(12), None)

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_valid_user_failure(self, mock):
        mock.return_value = None
        self.assertFalse(validUser(985))

        mock.return_value = ()
        self.assertFalse(validUser(985))

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_valid_user_success(self, mock):
        mock.return_value = ((985, "king_jerma985_of_jermalonia", "jerma985@jerma.com", "secret_password"))
        self.assertTrue(validUser(985))

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_get_username(self, mock):
        mock.return_value = (('jerma985',),)
        self.assertEqual(getUsername(985), "jerma985")

if __name__ == '__main__':
    unittest.main()