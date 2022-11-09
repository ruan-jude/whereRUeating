import mariadb
from DatabaseServices import setup_cursor, isolate_first_value_from_tuple
from AccountServices import get_user_preferences

#TODO: Finish this later
def searchMenuItems(search_term, current_user):
    whitelist, blacklist = get_user_preferences(current_user)


def getMenuItems(requested_date, restaurant_name, meal_time):
    cursor, read_conn = setup_cursor("read")
    query = """SELECT dishes.name, menuItems.date, menuItems.meal_time 
            FROM menuItems 
            INNER JOIN dishes ON menuItems.dish_id = dishes.id 
            INNER JOIN restaurants ON restaurants.id = menuItems.restaurant_id 
            WHERE restaurants.name = ? AND menuItems.date = ? AND menuItems.meal_time = ?"""
    cursor.execute(query, (restaurant_name, requested_date, meal_time))
    result_set = cursor.fetchall() 

    isolated_dish_names = isolate_first_value_from_tuple(result_set)

    read_conn.close()
    return isolated_dish_names

def selectDishesBasedOnTags(tagList):
    #SELECT dishes.name FROM dishes INNER JOIN dishInfo ON dishes.id = dishInfo.dish_id WHERE dishInfo.tag_name = '' OR WHERE dishInfo.tag_name = '' OR WHERE dishInfo.tag_name = '' OR WHERE dishInfo.tag_name = ''

    baseQuery = "SELECT dishes.name FROM dishes INNER JOIN dishInfo ON dishes.id = dishInfo.dish_id"
    whereClause = " WHERE dishInfo.tag_name = ?"
    cursor, read_conn = setup_cursor("read")

    for tag in tagList:
        #print(tag)
        baseQuery = baseQuery + whereClause
        if tagList.index(tag) == 0:
            whereClause = " OR dishInfo.tag_name = ?" 

    #print(baseQuery)
    cursor.execute(baseQuery, tagList)
    result_set = cursor.fetchall()
    print(result_set)
    read_conn.close()
    return result_set

def selectDishesExcludingTags(tagList):
    baseQuery = "SELECT dishes.name FROM dishes INNER JOIN dishInfo ON dishes.id = dishInfo.dish_id"
    whereClause = " WHERE dishInfo.tag_name <> ?"
    cursor, read_conn = setup_cursor("read")

    for tag in tagList:
        #print(tag)
        baseQuery = baseQuery + whereClause
        if tagList.index(tag) == 0:
            whereClause = " AND dishInfo.tag_name <> ?" 

    #print(baseQuery)
    cursor.execute(baseQuery, tagList)
    result_set = cursor.fetchall()
    print(result_set)
    read_conn.close()
    return result_set

# SELECT dishes.name FROM dishes 
# INNER JOIN dishInfo ON dishes.id = dishInfo.dish_id 
# INNER JOIN menuItems ON menuItems.dish_id = dishes.id
# WHERE dishInfo.tag_name = ?;
# SELECT dishes.name FROM dishes INNER JOIN dishInfo ON dishes.id = dishInfo.dish_id WHERE dishInfo.tag_name = ?;

def selectMenuItemsWithUserPreferences(current_user, requested_date, meal_time):
    user_whitelist, user_blacklist = get_user_preferences(current_user)
    cursor, read_conn = setup_cursor("read")

    # [brower, livingston, busch, nielson]
    # dining_hall_ids = [1, 2, 3, 4] 
    # These magic numbers aren't good practice
    # not proud of this mess here
    brower_query = selectMenuItemsIncludingTags(user_whitelist, 1, requested_date, meal_time) + " INTERSECT " + selectMenuItemsExcludingTags(user_blacklist, 1, requested_date, meal_time)
    livingston_query = selectMenuItemsIncludingTags(user_whitelist, 2, requested_date, meal_time) + " INTERSECT " + selectMenuItemsExcludingTags(user_blacklist, 2, requested_date, meal_time)
    busch_query = selectMenuItemsIncludingTags(user_whitelist, 3, requested_date, meal_time) + " INTERSECT " + selectMenuItemsExcludingTags(user_blacklist, 3, requested_date, meal_time)
    nielson_query = selectMenuItemsIncludingTags(user_whitelist, 4, requested_date, meal_time) + " INTERSECT " + selectMenuItemsExcludingTags(user_blacklist, 4, requested_date, meal_time)

    cursor.execute(brower_query)
    full_brower_list = cursor.fetchall().isolate_first_value_from_tuple()

    cursor.execute(livingston_query)
    full_livingston_list = cursor.fetchall().isolate_first_value_from_tuple()

    cursor.execute(busch_query)
    full_busch_list = cursor.fetchall().isolate_first_value_from_tuple()

    cursor.execute(nielson_query)
    full_nielson_list = cursor.fetchall().isolate_first_value_from_tuple()

    full_result_set = [full_brower_list, full_livingston_list, full_busch_list, full_nielson_list]

    read_conn.close()
    return full_result_set

def selectMenuItemsIncludingTags(tagList, dining_hall, requested_date, meal_time):
    baseQuery = f"""SELECT dishes.name, dishInfo.tag_name, restaurants.name 
        FROM menuItems 
        INNER JOIN dishInfo ON menuItems.dish_id = dishInfo.dish_id 
        INNER JOIN dishes ON menuItems.dish_id = dishes.id 
        INNER JOIN restaurants ON restaurants.id = menuItems.restaurant_id 
        WHERE restaurants.name = {dining_hall} AND menuItems.date = {requested_date} 
        AND menuItems.meal_time = {meal_time} AND ("""

    # I'm not proud of this: Passing in raw strings like this to queries is not a good idea.
    # Always parameterize queries with inputs like this.   
    for tag in tagList:
        #print(tag)
        # baseQuery = baseQuery + whereClause
        whereClause = ""
        if tagList.index(tag) == 0:
            whereClause = f"WHERE dishInfo.tag_name = '{tag}'"
        else:
            whereClause - f" OR dishInfo.tag_name = '{tag}'"
        baseQuery = baseQuery + whereClause


    baseQuery = baseQuery + ")"

    #print(baseQuery)
    # cursor.execute(baseQuery, tagList)
    # result_set = cursor.fetchall()
    # print(result_set)
    # read_conn.close()
    return baseQuery

def selectMenuItemsExcludingTags(tagList, dining_hall, requested_date, meal_time):
    baseQuery = f"""SELECT dishes.name, dishInfo.tag_name, restaurants.name 
        FROM menuItems 
        INNER JOIN dishInfo ON menuItems.dish_id = dishInfo.dish_id 
        INNER JOIN dishes ON menuItems.dish_id = dishes.id 
        INNER JOIN restaurants ON restaurants.id = menuItems.restaurant_id 
        WHERE restaurants.name = {dining_hall} AND menuItems.date = {requested_date} 
        AND menuItems.meal_time = {meal_time} AND ("""
    # whereClause = "dishInfo.tag_name <> ?"
    # cursor, read_conn = setup_cursor("read")

    for tag in tagList:
        #print(tag)
        # baseQuery = baseQuery + whereClause
        whereClause = ""
        if tagList.index(tag) == 0:
            whereClause = f"WHERE dishInfo.tag_name <> '{tag}'"
        else:
            whereClause - f" OR dishInfo.tag_name <> '{tag}'"
        baseQuery = baseQuery + whereClause

    baseQuery = baseQuery + ")"

    #print(baseQuery)
    # cursor.execute(baseQuery, tagList)
    # result_set = cursor.fetchall()
    # print(result_set)
    # read_conn.close()
    return baseQuery

# Get the names of all of the dishes being served that have tag_name = ?
# SELECT menuItems.dish_id, dishes.name, dishInfo.tag_name FROM menuItems
# INNER JOIN dishInfo ON menuItems.dish_id = dishInfo.dish_id 
# INNER JOIN dishes ON menuItems.dish_id = dishes.id
# WHERE dishInfo.tag_name = ?;
# SELECT menuItems.dish_id, dishes.name, dishInfo.tag_name FROM menuItems INNER JOIN dishInfo ON menuItems.dish_id = dishInfo.dish_id INNER JOIN dishes ON menuItems.dish_id = dishes.id WHERE dishInfo.tag_name = ?;


def main():
    getMenuItems("something", "restaurant_name")
    selectDishesBasedOnTags(("tag", "tag1", "tag2", "tag3"))
    selectMenuItemsIncludingTags(("tag", "tag1", "tag2", "tag3"))

if __name__ == "__main__":
    main()