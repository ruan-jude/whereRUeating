import unittest
import sys
from unittest import mock
from unittest.mock import patch
if __name__ == '__main__':
    import constants
else:    
    import test.constants as constants
import mariadb

sys.path.insert(1, constants.PATH_TO_PROJECT)
#print(sys.path)

from server.AccountServices import *
from server.DishServices import *

class TestDishServices(unittest.TestCase):

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_check_valid_dish(self, mock):
        mock.return_value = ((1, "paratha"),)
        self.assertTrue(checkValidDish(1))

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_check_valid_dish_false(self, mock):
        mock.return_value = ()
        self.assertFalse(checkValidDish(123))

        mock.return_value = None
        self.assertFalse(checkValidDish(123))

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_get_all_dishes(self, mock):
        expected_list = ((1, "kosher salt"), (2, "spicy chicken nuggets"), (3, "sushi"))
        mock.return_value = expected_list
        self.assertEqual(getAllDishes(), expected_list)

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_get_restaurant_name(self, mock):
        mock.return_value = (("Potion of Fire Resistance",), )
        self.assertEqual(getDishName(512), "Potion of Fire Resistance")


    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_get_dish_tags(self, mock):
        mock.return_value = (("kosher",), ("spicy",), ("some_tag", ))
        expected_list = ["kosher", "spicy", "some_tag"]
        self.assertEqual(getDishTags(1), expected_list)

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_add_dish_tags(self, mock):
        some_id = 1
        some_tags = ("Krusty Krab", "Jerma", "Peeped horror")
        addDishTags(some_id, some_tags)
        self.assertEqual(mock.call_count, len(some_tags))

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_add_dish_tags_empty_tag_list(self, mock):
        some_id = 1
        some_tags = ()
        addDishTags(some_id, some_tags)
        self.assertEqual(mock.call_count, len(some_tags))

    @mock.patch.object(mariadb.Cursor, "execute")
    def test_clear_dish_tags(self, mock):
        delete_query = "DELETE FROM dishInfo WHERE dish_id=?"
        some_id = 1
        clearDishTags(some_id)
        mock.assert_called_with(delete_query, (some_id,))

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

        test_return = getMenuItemsWithPreferences(test_user, restaurant_name, test_date, meal_time)
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

        return_query = selectMenuItemsWithTags(1, test_tagList, test_dh, test_date, test_meal)
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

        return_query = selectMenuItemsWithTags(0, test_tagList, test_dh, test_date, test_meal)
        self.assertEqual(return_query.replace('\n', "").replace(" ", ''), full_query.replace('\n', "").replace(" ", ''))

    @mock.patch.object(mariadb.Cursor, "fetchall")
    def test_get_all_tags(self, mock):
        mock.return_value = (("kosher",), ("spicy",), ("some_tag", ))
        expected_list = ["kosher", "spicy", "some_tag"]
        self.assertEqual(getAllTags(), expected_list)

if __name__ == '__main__':
    unittest.main()