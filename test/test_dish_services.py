import unittest
import sys
from unittest import mock
from unittest.mock import patch
import test.constants as constants
import mariadb

sys.path.insert(1, constants.PATH_TO_PROJECT)
#print(sys.path)

from server.AccountServices import *
from server.DishServices import *

class TestDishServices(unittest.TestCase):

    @mock.patch.object(mariadb.Cursor, "fetchall")
    @unittest.skip("function not implemented")
    def test_search_menu_tems(self, mock):
        mock.return_value = [("result_set",), ("result_set")]
        search_term = "test_term"
        current_user = "Some person"
        searchMenuItems(search_term, current_user)
        mock.assert_called()

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_get_menu_items(self, mock):
        mock.return_value = [("result_set",), ("result_set",)]
        expected_return = ["result_set", "result_set"]
        
        test_date = "2022-11-05"
        restaurant_name = "Livingston DH"
        meal_time = "breakfast"
        
        test_return = getMenuItems(test_date, restaurant_name, meal_time)
        mock.assert_called()
        self.assertEqual(test_return, expected_return)


    @patch("mariadb.Cursor.fetchall")
    @patch("mariadb.Cursor.execute")
    def test_get_menu_items_with_user_preferences(self, mock_fetch, mock_execute):
        mock_execute.return_value = [("result_set",), ("result_set",)]
        mock_fetch.return_value = ["result_set", "result_set"]

        test_user = "Jerma985"
        test_date = "2022-11-05"
        restaurant_name = "Livingston DH"
        meal_time = "breakfast"

        test_return = getMenuItemsWithUserPreferences(test_user, restaurant_name, test_date, meal_time)
        mock_fetch.assert_called()
        mock_execute.assert_called()
        self.assertEqual(test_return, mock_fetch.return_value)

    def test_select_menu_items_including_tags(self):
        test_tagList = ["tag1", "tag2"]
        test_dh = "Nielson DH"
        test_date = "2022-09-19"
        test_meal = "Breakfast"
        
        full_query = f"""SELECT dishes.name, dishInfo.tag_name, restaurants.name 
            FROM menuItems 
            INNER JOIN dishInfo ON menuItems.dish_id = dishInfo.dish_id 
            INNER JOIN dishes ON menuItems.dish_id = dishes.id 
            INNER JOIN restaurants ON restaurants.id = menuItems.restaurant_id 
            WHERE restaurants.name = 'Nielson DH' AND menuItems.date = '2022-09-19' 
            AND menuItems.meal_time = 'Breakfast' AND (dishInfo.tag_name = 'tag1' OR dishInfo.tag_name = 'tag2')"""

        return_query = selectMenuItemsIncludingTags(test_tagList, test_dh, test_date, test_meal)
        self.assertEqual(return_query.replace('\n', "").replace(" ", ''), full_query.replace('\n', "").replace(" ", ''))

    def test_select_menu_items_excluding_tags(self):
        test_tagList = ["tag1", "tag2"]
        test_dh = "Nielson DH"
        test_date = "2022-09-19"
        test_meal = "Breakfast"
        
        full_query = f"""SELECT dishes.name, dishInfo.tag_name, restaurants.name 
            FROM menuItems 
            INNER JOIN dishInfo ON menuItems.dish_id = dishInfo.dish_id 
            INNER JOIN dishes ON menuItems.dish_id = dishes.id 
            INNER JOIN restaurants ON restaurants.id = menuItems.restaurant_id 
            WHERE restaurants.name = 'Nielson DH' AND menuItems.date = '2022-09-19' 
            AND menuItems.meal_time = 'Breakfast' AND (dishInfo.tag_name <> 'tag1' OR dishInfo.tag_name <> 'tag2')"""

        return_query = selectMenuItemsExcludingTags(test_tagList, test_dh, test_date, test_meal)
        self.assertEqual(return_query.replace('\n', "").replace(" ", ''), full_query.replace('\n', "").replace(" ", ''))

    def test_isolate_date(self):
        test_date = "2022-09-19 00:00:00"
        return_date = isolate_date(test_date)
        expected_date = "2022-09-19"
        self.assertEqual(return_date, expected_date)

if __name__ == '__main__':
    unittest.main()