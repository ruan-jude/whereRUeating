import mariadb
from server.DatabaseServices import setup_cursor, isolate_first_value_from_tuple
from server.AccountServices import get_user_preferences

#TODO: Finish this later
def searchMenuItems(search_term, current_user):
    whitelist, blacklist = get_user_preferences(current_user)

'''
Gets all tag names
FUNCTIONING
'''
def getAllTags():
    cursor, read_conn = setup_cursor("read")
    cursor.execute("SELECT tags.name FROM tags")
    result_set = cursor.fetchall()
    read_conn.close()

    return [tag[0] for tag in result_set]

'''
Gets all menu items
FUNCTIONING
'''
def getAllMenuItems():
    cursor, read_conn = setup_cursor("read")
    cursor.execute("SELECT * FROM dishes")
    result_set = cursor.fetchall()
    read_conn.close()

    return result_set

'''
Gets all tags associated with a given menu item
FUNCTIONING
'''
def getDishTags(dishID):
    cursor, read_conn = setup_cursor("read")
    cursor.execute("SELECT dishInfo.tag_name FROM dishInfo WHERE dishInfo.dish_id = ?", (dishID, ))
    result_set = cursor.fetchall()
    read_conn.close()
    
    return [tag[0] for tag in result_set]

'''
Inserts the tags of specified dish
FUNCTIONING
'''
def addDishTags(dishID, dishTags):
    cursor,write_conn = setup_cursor("write")

    for tag in dishTags:
        cursor.execute("INSERT IGNORE INTO dishInfo (dish_id, tag_name) VALUES (?, ?)", (dishID, tag))

    write_conn.commit()
    write_conn.close()

'''
Deletes tags of specified dish
FUNCTIONING
'''
def clearDishTags(dishID):
    cursor, delete_conn = setup_cursor("write")
    cursor.execute("DELETE FROM dishInfo WHERE dish_id=?", (dishID,))
    delete_conn.commit()
    delete_conn.close()

'''
Gets name of the specified dish
FUNCTIONING
'''
def getDishName(dishID):
    cursor, read_conn = setup_cursor("read")
    cursor.execute("SELECT dishes.name FROM dishes WHERE dishes.id = ?", (dishID, ))
    result_set = cursor.fetchall()
    read_conn.close()

    return result_set[0][0]

def validDish(dishID):
    cursor, read_conn = setup_cursor("read")
    cursor.execute("SELECT * FROM dishes WHERE dishes.id = ?", (dishID, ))
    result_set = cursor.fetchall()

    if result_set == None or not result_set:
        return False
    
    return True


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

def getMenuItemsWithUserPreferences(current_user, restaurant_name, requested_date, meal_time):
    user_whitelist, user_blacklist = get_user_preferences(current_user)
    cursor, read_conn = setup_cursor("read")
    retrieved_date = isolate_date(requested_date)
    full_query = selectMenuItemsIncludingTags(user_whitelist, restaurant_name, retrieved_date, meal_time) + " INTERSECT " + selectMenuItemsExcludingTags(user_blacklist, restaurant_name, retrieved_date, meal_time)

    cursor.execute(full_query)
    result_set = isolate_first_value_from_tuple(cursor.fetchall())
    
    read_conn.close()
    return result_set

'''

'''
def selectMenuItemsIncludingTags(tagList, dining_hall, requested_date, meal_time):
    baseQuery = f"""SELECT dishes.name, dishInfo.tag_name, restaurants.name 
        FROM menuItems 
        INNER JOIN dishInfo ON menuItems.dish_id = dishInfo.dish_id 
        INNER JOIN dishes ON menuItems.dish_id = dishes.id 
        INNER JOIN restaurants ON restaurants.id = menuItems.restaurant_id 
        WHERE restaurants.name = '{dining_hall}' AND menuItems.date = '{requested_date}' 
        AND menuItems.meal_time = '{meal_time}' AND ("""

    # I'm not proud of this: Passing in raw strings like this to queries is not a good idea.
    # Always parameterize queries with inputs like this.   
    for tag in tagList:
        whereClause = ""
        if tagList.index(tag) == 0:
            whereClause = f"dishInfo.tag_name = '{tag}'"
        else:
            whereClause = f" OR dishInfo.tag_name = '{tag}'"
        baseQuery = baseQuery + whereClause


    baseQuery = baseQuery + ")"
    return baseQuery

def selectMenuItemsExcludingTags(tagList, dining_hall, requested_date, meal_time):
    baseQuery = f"""SELECT dishes.name, dishInfo.tag_name, restaurants.name 
        FROM menuItems 
        INNER JOIN dishInfo ON menuItems.dish_id = dishInfo.dish_id 
        INNER JOIN dishes ON menuItems.dish_id = dishes.id 
        INNER JOIN restaurants ON restaurants.id = menuItems.restaurant_id 
        WHERE restaurants.name = '{dining_hall}' AND menuItems.date = '{requested_date}' 
        AND menuItems.meal_time = '{meal_time}' AND ("""

    for tag in tagList:
        whereClause = ""
        if tagList.index(tag) == 0:
            whereClause = f"dishInfo.tag_name <> '{tag}'"
        else:
            whereClause = f" OR dishInfo.tag_name <> '{tag}'"
        baseQuery = baseQuery + whereClause

    baseQuery = baseQuery + ")"
    return baseQuery

def isolate_date(raw_date):
    strdate = str(raw_date)
    #print(strdate[:10])
    return strdate[:10]

def main():
    getMenuItems("something", "restaurant_name")
    selectMenuItemsIncludingTags(("tag", "tag1", "tag2", "tag3"))

if __name__ == "__main__":
    main()