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
        self.assertEqual(checkDiningHallsBusy(), return_message)

    @mock.patch('datetime.datetime', wraps=datetime)
    def test_check_dining_halls_busy_13_20(self, mock):
        mock.now.return_value = mocked_now(13, 20)
        return_message = "Classes just ended at 01:20 PM, so the dining halls might get/be busy now."
        self.assertEqual(checkDiningHallsBusy(), return_message)

    @mock.patch('datetime.datetime', wraps=datetime)
    def test_check_dining_halls_busy_15_20(self, mock):
        mock.now.return_value = mocked_now(15, 20)
        return_message = "Classes just ended at 03:20 PM, so the dining halls might get/be busy now."
        self.assertEqual(checkDiningHallsBusy(), return_message)

    @mock.patch('datetime.datetime', wraps=datetime)
    def test_check_dining_halls_busy_18_00(self, mock):
        mock.now.return_value = mocked_now(18, 0)
        return_message = "Classes just ended at 06:00 PM, so the dining halls might get/be busy now."
        self.assertEqual(checkDiningHallsBusy(), return_message)

    @mock.patch('datetime.datetime', wraps=datetime)
    def test_check_dining_halls_busy_10_00(self, mock):
        mock.now.return_value = mocked_now(10, 0)
        return_message = "Dining halls are probably not busy at this time."
        self.assertEqual(checkDiningHallsBusy(), return_message)

    @mock.patch('datetime.datetime', wraps=datetime)
    def test_check_dining_halls_busy_14_20(self, mock):
        mock.now.return_value = mocked_now(14, 20)
        return_message = "Dining halls are probably not busy at this time."
        self.assertEqual(checkDiningHallsBusy(), return_message)

    @mock.patch('datetime.datetime', wraps=datetime)
    def test_check_dining_halls_busy_19_00(self, mock):
        mock.now.return_value = mocked_now(19, 00)
        return_message = "Dining halls are probably not busy at this time."
        self.assertEqual(checkDiningHallsBusy(), return_message)

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_check_valid_restaurant_success(self, mock):
        mock.return_value = True
        self.assertTrue(checkValidRestaurant("some_id_not_important"))

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_check_valid_restaurant_failure(self, mock):
        mock.return_value = False
        self.assertFalse(checkValidRestaurant("some_id_not_important"))

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_get_restaurant_address(self, mock):
        mock.return_value = (("124 Conch Street, Bikini Bottom, NJ",),)
        self.assertEqual(getRestaurantAddress(123), "124 Conch Street, Bikini Bottom, NJ")

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_get_off_campus_restaurants(self, mock):
        mock.return_value = ((12, "Krusty Krab", "124 Conch Street, Bikini Bottom, NJ"), (11, "The Stray Sheep", "Somewhere in NA"))
        expected_dict = {12: ("Krusty Krab", "124 Conch Street, Bikini Bottom, NJ"), 11: ("The Stray Sheep", "Somewhere in NA")}
        self.assertEqual(getOffCampusRestaurants(), expected_dict)

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_get_restaurant_id(self, mock):
        mock.return_value = ((123,), )
        self.assertEqual(getRestaurantID("Jermalonia"), 123)

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_get_restaurant_name(self, mock):
        mock.return_value = (("The Bar",), )
        self.assertEqual(getRestaurantName(123), "The Bar")

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_get_restaurant_address(self, mock):
        mock.return_value = (("124 Jerma Dollhouse",), )
        self.assertEqual(getRestaurantAddress(124), "124 Jerma Dollhouse")

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_get_restaurants_using_tags_both_lists(self, mock):
        mock.return_value = (("Krusty Krab", "124 Conch Street, Bikini Bottom, NJ"), ("The Stray Sheep", "Somewhere in NA"))
        expected_dict = {"Krusty Krab" : "124 Conch Street, Bikini Bottom, NJ", "The Stray Sheep" : "Somewhere in NA"}
        self.assertEqual(getRestaurantsUsingTags(("asdf", "asdf"), ("asdf", "asdfasdfasdf")), expected_dict)

    @patch("server.DiningServices.getOffCampusRestaurants")
    def test_get_restaurants_using_tags_both_lists(self, mock):
        getRestaurantsUsingTags(None, None)
        mock.assert_called()

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_check_restaurant_exists_true(self, mock):
        mock.return_value = (("Krusty Krab", "124 Conch Street, Bikini Bottom, NJ"), ("The Stray Sheep", "Somewhere in NA"))
        self.assertTrue(checkRestaurantExists("Krusty Krab"))
        
    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_check_restaurant_exists_false(self, mock):
        mock.return_value = ()
        self.assertFalse(checkRestaurantExists("Krusty Krab"))

        mock.return_value = None
        self.assertFalse(checkRestaurantExists("Krusty Krab"))
    
    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_check_valid_restaurant(self, mock):
        mock.return_value = (("Krusty Krab", "124 Conch Street, Bikini Bottom, NJ"), ("The Stray Sheep", "Somewhere in NA"))
        self.assertTrue(checkValidRestaurant(123))

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_check_restaurant_exists_false(self, mock):
        mock.return_value = ()
        self.assertFalse(checkValidRestaurant(123))

        mock.return_value = None
        self.assertFalse(checkValidRestaurant(123))

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_insert_restaurant_on_campus(self, mock):
        insert_query = "INSERT INTO restaurants (name, on_campus, address) VALUES (?, ?, ?)"
        test_restaurant_on_campus = True
        test_restaurant_name = "Mos Eisley Cantina"
        test_address = "Mos Eisley, Tatooine, Outer Rim"
        insertRestaurant(test_restaurant_name, test_restaurant_on_campus, test_address)
        mock.assert_called_with(insert_query, (test_restaurant_name, test_restaurant_on_campus, test_address))

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_insert_restaurant_off_campus(self, mock):
        insert_query = "INSERT INTO restaurants (name, on_campus, address) VALUES (?, ?, ?)"
        test_restaurant_on_campus = False
        test_restaurant_name = "Mos Eisley Cantina"
        test_address = "Mos Eisley, Tatooine, Outer Rim"
        insertRestaurant(test_restaurant_name, test_restaurant_on_campus, test_address)
        mock.assert_called_with(insert_query, (test_restaurant_name, test_restaurant_on_campus, test_address))

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_update_restaurant_off_campus(self, mock):
        update_query = "UPDATE restaurants SET name = ?, address = ? WHERE id = ?"
        test_restaurant_id = 1
        test_restaurant_name = "Mos Eisley Cantina"
        test_address = "Mos Eisley, Tatooine, Outer Rim"
        updateRestaurantInfo(test_restaurant_id, test_restaurant_name, test_address)
        mock.assert_called_with(update_query, (test_restaurant_name, test_address, test_restaurant_id))

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_delete_restaurant_off_campus(self, mock):
        delete_query = "DELETE FROM restaurants WHERE id = ?"
        test_restaurant_id = 1
        deleteRestaurant(test_restaurant_id)
        mock.assert_called_with(delete_query, (test_restaurant_id,))

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_get_restaurant_tags(self, mock):
        mock.return_value = (("kosher",), ("spicy",), ("some_tag", ))
        expected_list = ["kosher", "spicy", "some_tag"]
        self.assertEqual(getRestaurantTags(1), expected_list)

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_add_restaurant_tags(self, mock):
        some_id = 1
        some_tags = ("Krusty Krab", "Jerma", "Peeped horror")
        addRestaurantTags(some_id, some_tags)
        self.assertEqual(mock.call_count, len(some_tags))

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_add_restaurant_tags_empty_tag_list(self, mock):
        some_id = 1
        some_tags = ()
        addRestaurantTags(some_id, some_tags)
        self.assertEqual(mock.call_count, len(some_tags))

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_delete_restaurant(self, mock):
        delete_query = "DELETE FROM restaurantInfo WHERE restaurant_id = ?"
        some_id = 1
        clearRestaurantTags(some_id)
        mock.assert_called_with(delete_query, (some_id,))

if __name__ == '__main__':
    unittest.main()