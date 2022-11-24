import calendar
from datetime import datetime
from server.DatabaseServices import setup_cursor, isolate_first_value_from_tuple
from server.AccountServices import get_user_preferences

ITEMS_TO_CHECK = ['chicken', 'pork', 'beef', 'seafood', 'dairy', 'nuts', 'chinese', 'indian', 'mexican', 'italian', 'japanese', 'cafe']
DB_DH_STR = {"Livingston":"Livingston DH", "Busch":"Busch DH", "Brower":"Brower DH", "Nielson":"Nielson DH"}
MEAL_TIMES = ['breakfast', 'lunch', 'dinner']

# ===== DISH FUNCTIONS =====
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

'''
Checks whether a dish id is valid
FUNCTIONING
'''
def validDish(dishID):
    cursor, read_conn = setup_cursor("read")
    cursor.execute("SELECT * FROM dishes WHERE dishes.id = ?", (dishID, ))
    result_set = cursor.fetchall()
    read_conn.close()

    if result_set == None or not result_set: return False
    
    return True
# =======================

# ===== MENU FUNCTIONS =====
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
Gets menu items at the given restaurant, on a given date, at a specific meal time
FUNCTIONING
'''
def getMenuItems(restaurant_name, requested_date, meal_time):
    cursor, read_conn = setup_cursor("read")
    query = """SELECT dishes.name, menuItems.date, menuItems.meal_time 
            FROM menuItems 
            INNER JOIN dishes ON menuItems.dish_id = dishes.id 
            INNER JOIN restaurants ON restaurants.id = menuItems.restaurant_id 
            WHERE restaurants.name = ? AND menuItems.date = ? AND menuItems.meal_time = ?"""
    cursor.execute(query, (restaurant_name, requested_date, meal_time))
    result_set = cursor.fetchall() 
    read_conn.close()

    isolated_dish_names = isolate_first_value_from_tuple(result_set)
    return isolated_dish_names

'''
Gets menu items at the given restaurant, on a given date, at a specific meal time
Includes user preferences
FUNCTIONING
'''
def getMenuItemsWithUserPreferences(current_user_id, restaurant_name, requested_date, meal_time):
    user_whitelist, user_blacklist = get_user_preferences(current_user_id)
    cursor, read_conn = setup_cursor("read")
    retrieved_date = requested_date #isolate_date(requested_date)
    full_query = selectMenuItemsIncludingTags(user_whitelist, restaurant_name, retrieved_date, meal_time) + " INTERSECT " + selectMenuItemsExcludingTags(user_blacklist, restaurant_name, retrieved_date, meal_time)

    cursor.execute(full_query)
    result_set = isolate_first_value_from_tuple(cursor.fetchall())
    
    read_conn.close()
    return result_set

'''
Gets menu items with the given whitelist and blacklist
'''
def getMenuItemsWithPreferences(restaurant_name, requested_date, meal_time, whitelist, blacklist):
    cursor, read_conn = setup_cursor("read")
    retrieved_date = requested_date #isolate_date(requested_date)
    full_query = selectMenuItemsIncludingTags(whitelist, restaurant_name, retrieved_date, meal_time) + " INTERSECT " + selectMenuItemsExcludingTags(blacklist, restaurant_name, retrieved_date, meal_time)

    cursor.execute(full_query)
    result_set = isolate_first_value_from_tuple(cursor.fetchall())
    
    read_conn.close()
    return result_set

#TODO: Finish this later
def searchMenuItems(restaurantsIncluded, whitelist, blacklist):    
    menuDays, _ = getDateStr()
    dateDatetimes = [(i, day[1]) for i, day in enumerate(menuDays)]

    completeSearch = dict()
    for restaurant in restaurantsIncluded:
        restaurantMeals = dict()
        for (dateID, dateDatetime) in dateDatetimes:
            timeMenus = dict()
            for time in MEAL_TIMES:
                timeMenus[time] = getMenuItemsWithPreferences(DB_DH_STR[restaurant], dateDatetime, time, whitelist, blacklist)
                if not bool(timeMenus[time]): timeMenus[time]=False
            if all(value == False for value in timeMenus.values()): restaurantMeals[dateID] = False
            else: restaurantMeals[dateID] = timeMenus
        completeSearch[restaurant] = restaurantMeals

    return completeSearch

'''
Gets menu items with included tags
FUNCTIONING
'''
def selectMenuItemsIncludingTags(tagList, dining_hall, requested_date, meal_time):
    baseQuery = f"""SELECT dishes.name, dishInfo.tag_name, restaurants.name 
        FROM menuItems 
        INNER JOIN dishInfo ON menuItems.dish_id = dishInfo.dish_id 
        INNER JOIN dishes ON menuItems.dish_id = dishes.id 
        INNER JOIN restaurants ON restaurants.id = menuItems.restaurant_id 
        WHERE restaurants.name = '{dining_hall}' AND menuItems.date = '{requested_date}' 
        AND menuItems.meal_time = '{meal_time}'"""

    if bool(tagList):
        # I'm not proud of this: Passing in raw strings like this to queries is not a good idea.
        # Always parameterize queries with inputs like this.   
        baseQuery = baseQuery + " AND ("
        for tag in tagList:
            whereClause = ""
            if tagList.index(tag) == 0:
                whereClause = f"dishInfo.tag_name = '{tag}'"
            else:
                whereClause = f" OR dishInfo.tag_name = '{tag}'"
            baseQuery = baseQuery + whereClause
        baseQuery = baseQuery + ")"

    return baseQuery

'''
Gets menu items with excluded tags
FUNCTIONING
'''
def selectMenuItemsExcludingTags(tagList, dining_hall, requested_date, meal_time):
    baseQuery = f"""SELECT dishes.name, dishInfo.tag_name, restaurants.name 
        FROM menuItems 
        INNER JOIN dishInfo ON menuItems.dish_id = dishInfo.dish_id 
        INNER JOIN dishes ON menuItems.dish_id = dishes.id 
        INNER JOIN restaurants ON restaurants.id = menuItems.restaurant_id 
        WHERE restaurants.name = '{dining_hall}' AND menuItems.date = '{requested_date}' 
        AND menuItems.meal_time = '{meal_time}'"""
    
    if bool(tagList): 
        baseQuery = baseQuery + " AND ("
        for tag in tagList:
            whereClause = ""
            if tagList.index(tag) == 0:
                whereClause = f"dishInfo.tag_name <> '{tag}'"
            else:
                whereClause = f" OR dishInfo.tag_name <> '{tag}'"
            baseQuery = baseQuery + whereClause
        baseQuery = baseQuery + ")"

    return baseQuery
# ======================

# ===== OTHER FUNCTIONS =====
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
Gets the menu dates that were scraped with connected strings
Returns menuDays where each item = (dayStr, day)
FUNCTIONING
'''
def getDateStr():
    cursor, read_conn = setup_cursor("read")
    cursor.execute("SELECT DISTINCT(date) from menuItems ORDER BY date")
    result_set = cursor.fetchall()
    read_conn.close()

    rawMenuDays = [date[0] for date in result_set]
    menuDays = list()
    for day in rawMenuDays:
        dayStr = calendar.day_name[day.weekday()] + ', ' + day.strftime('%B %d, %Y')
        menuDays.append((dayStr, day))

        # gets string for today's date
        if day.strftime('%B/%d/%Y') == datetime.now().strftime('%B/%d/%Y'): 
            todayStr = (dayStr, day)

    return menuDays, todayStr

def isolate_date(raw_date):
    strdate = str(raw_date)
    return strdate[:10]
# ===================