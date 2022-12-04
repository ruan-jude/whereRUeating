import calendar
from datetime import datetime
from server.HelperMethods import *
from server.DatabaseServices import *
from server.AccountServices import *

# ===== DISH FUNCTIONS =====
'''
Gets all menu items
'''
def getAllDishes():
    query = "SELECT * FROM dishes"

    cursor, readConn = setupCursor("read")
    cursor.execute(query)
    resultSet = cursor.fetchall()
    readConn.close()

    return resultSet

'''
Gets name of the specified dish
'''
def getDishName(dishID):
    query = "SELECT dishes.name FROM dishes WHERE dishes.id = ?"

    cursor, readConn = setupCursor("read")
    cursor.execute(query, (dishID, ))
    resultSet = cursor.fetchall()
    readConn.close()

    return resultSet[0][0]

'''
Gets all tags associated with a given dish
'''
def getDishTags(dishID):
    query = "SELECT dishInfo.tag_name FROM dishInfo WHERE dishInfo.dish_id = ?"

    cursor, readConn = setupCursor("read")
    cursor.execute(query, (dishID, ))
    resultSet = cursor.fetchall()
    readConn.close()

    return isolateFirstValueFromTuple(resultSet)

'''
Checks whether a dish id is valid
'''
def checkValidDish(dishID):
    query = "SELECT * FROM dishes WHERE dishes.id = ?"

    cursor, readConn = setupCursor("read")
    cursor.execute(query, (dishID, ))
    resultSet = cursor.fetchall()
    readConn.close()

    if resultSet == None or not resultSet: return False
    return True

'''
Inserts the tags of specified dish
'''
def addDishTags(dishID, dishTags):
    query = "INSERT IGNORE INTO dishInfo (dish_id, tag_name) VALUES (?, ?)"

    cursor, writeConn = setupCursor("write")
    for tag in dishTags:
        cursor.execute(query, (dishID, tag))
    writeConn.commit()
    writeConn.close()

'''
Deletes tags of specified dish
'''
def clearDishTags(dishID):
    query = "DELETE FROM dishInfo WHERE dish_id=?"

    cursor, deleteConn = setupCursor("write")
    cursor.execute(query, (dishID,))
    deleteConn.commit()
    deleteConn.close()

'''
Returns a list dateRes in the following format
    [(dateStr, [(DHStr, meal_time), ..., (DHStr, meal_time)]), ..., (dateStr, [(DHStr, meal_time), ..., (DHStr, meal_time)])]
'''
def getDishAvailability(dishID):
    query = "SELECT restaurant_id, date, meal_time FROM menuItems WHERE dish_id=? ORDER BY date, restaurant_id, meal_time"
    cursor, readConn = setupCursor("read")
    cursor.execute(query, (dishID,))
    resultSet = cursor.fetchall()
    readConn.close()

    # if no results, return None
    if not resultSet: return None

    # gets menu days
    menuDays, _ = getDateStrings()
    menuDaysStrings = {day[1]:day[0] for day in menuDays}

    # (DH_id, date.datetime, meal_time)
    prevDate = None
    dateRes, tempDateMenus = [], []
    for ind, item in enumerate(resultSet):
        # if at the front of the array set prevDate
        if ind == 0: prevDate = item[1]

        # new date, append prev info to dateRes and reset tempDateMenus
        if item[1] != prevDate:
            dateRes.append((menuDaysStrings[prevDate], tempDateMenus))
            tempDateMenus = []
        
        tempDateMenus.append((DB_DH_IDS[item[0]], item[2]))
        prevDate = item[1]
    # used to add last date info into the res
    dateRes.append((menuDaysStrings[prevDate], tempDateMenus))

    return dateRes
# =======================

# ===== MENU FUNCTIONS =====
'''
Gets menu items at the given restaurant, on a given date, at a specific meal time
'''
def getMenuItems(restaurantName, requestedDate, mealTime):
    query = """SELECT dishes.name, menuItems.date, menuItems.meal_time 
            FROM menuItems 
            INNER JOIN dishes ON menuItems.dish_id = dishes.id 
            INNER JOIN restaurants ON restaurants.id = menuItems.restaurant_id 
            WHERE restaurants.name = ? AND menuItems.date = ? AND menuItems.meal_time = ?"""

    cursor, readConn = setupCursor("read")
    cursor.execute(query, (restaurantName, requestedDate, mealTime))
    resultSet = cursor.fetchall()
    readConn.close()

    return isolateFirstValueFromTuple(resultSet)

'''
Gets menu items at the given restaurant, on a given date, at a specific meal time
Selects with whitelist and blacklist
'''
def getMenuItemsWithPreferences(restaurantName, requestedDate, mealTime, userID=None, whitelist=None, blacklist=None):
    if userID != None: whitelist, blacklist = getUserPreferences(userID)

    included = selectMenuItemsWithTags(1, whitelist, restaurantName, requestedDate, mealTime)
    excluded = selectMenuItemsWithTags(0, blacklist, restaurantName, requestedDate, mealTime)
    fullQuery = included + " INTERSECT " + excluded

    cursor, readConn = setupCursor("read")
    cursor.execute(fullQuery)
    resultSet = cursor.fetchall()
    readConn.close()

    return isolateFirstValueFromTuple(resultSet)

'''
Gets menu items with either the included or excluded tags
Selected from a given restaurant, on a specific date, at a specific time
    tagType == 1 IF getting INCLUDED
    tagType == 0 IF getting EXCLUDED
'''
def selectMenuItemsWithTags(tagType, tagList, restaurantName, requestedDate, mealTime):
    baseQuery = f"""SELECT dishes.name, dishInfo.tag_name, restaurants.name 
        FROM menuItems 
        INNER JOIN dishInfo ON menuItems.dish_id = dishInfo.dish_id 
        INNER JOIN dishes ON menuItems.dish_id = dishes.id 
        INNER JOIN restaurants ON restaurants.id = menuItems.restaurant_id 
        WHERE restaurants.name = '{restaurantName}' AND menuItems.date = '{requestedDate}' 
        AND menuItems.meal_time = '{mealTime}'"""
    
    if bool(tagList):
        baseQuery = baseQuery + " AND ("
        for tag in tagList:
            whereClause = ""
            if tagList.index(tag) == 0:
                whereClause = f"dishInfo.tag_name = '{tag}'" if tagType == 1 else f"dishInfo.tag_name <> '{tag}'"
            else:
                whereClause = f" OR dishInfo.tag_name = '{tag}'" if tagType == 1 else f" OR dishInfo.tag_name <> '{tag}'"
            baseQuery = baseQuery + whereClause
        baseQuery = baseQuery + ")"

    return baseQuery

'''
Search for all dishes following given preferences
'''
def searchForDish(restaurantsIncluded, whitelist, blacklist):    
    menuDays, _ = getDateStrings()
    dateDatetimes = [(i, day[1]) for i, day in enumerate(menuDays)]

    completeSearch = dict()
    for restaurant in restaurantsIncluded:
        restaurantMeals = dict()
        for (dateID, date) in dateDatetimes:
            timeMenus = dict()
            for time in MEAL_TIMES:
                timeMenus[time] = getMenuItemsWithPreferences(DB_DH_STR[restaurant], date, time, whitelist, blacklist)
                if not bool(timeMenus[time]): timeMenus[time]=False
            if all(value == False for value in timeMenus.values()): restaurantMeals[dateID] = False
            else: restaurantMeals[dateID] = timeMenus
        completeSearch[DB_DH_STR[restaurant]] = restaurantMeals

    return completeSearch
# ======================

# ===== OTHER FUNCTIONS =====
'''
Gets all tag names
'''
def getAllTags():
    query = "SELECT tags.name FROM tags"

    cursor, readConn = setupCursor("read")
    cursor.execute(query)
    resultSet = cursor.fetchall()
    readConn.close()

    return isolateFirstValueFromTuple(resultSet)

'''
Gets the menu dates that were scraped with connected strings
Returns menuDays where each item = (dayStr, day)
'''
def getDateStrings():
    query = "SELECT DISTINCT(date) from menuItems ORDER BY date"
    cursor, readConn = setupCursor("read")
    cursor.execute(query)
    resultSet = cursor.fetchall()
    readConn.close()

    rawMenuDays = isolateFirstValueFromTuple(resultSet)
    menuDays = list()
    todayString = ((calendar.day_name[rawMenuDays[0].weekday()] + ', ' + rawMenuDays[0].strftime('%B %d, %Y')), rawMenuDays[0])  # defaults to first day of the week

    for day in rawMenuDays:
        dayString = calendar.day_name[day.weekday()] + ', ' + day.strftime('%B %d, %Y')
        menuDays.append((dayString, day))

        # gets string for today's date
        if day.strftime('%B/%d/%Y') == datetime.now().strftime('%B/%d/%Y'): 
            todayString = (dayString, day)

    return menuDays, todayString
# ===================
