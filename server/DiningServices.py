import datetime
from server.HelperMethods import *
from server.DatabaseServices import *

BUSY_CLASS_END_TIMES = [datetime.time(11,40,0), datetime.time(13,20, 0), datetime.time(15,20,0), datetime.time(18,0,0)]

# ===== BUSY DH =====
def checkDiningHallsBusy():
    currentTime = datetime.datetime.now()
    currentMinute = currentTime.minute
    currentHour = currentTime.hour

    for endTime in BUSY_CLASS_END_TIMES:
        if (currentHour - endTime.hour) == 0 and currentMinute >= endTime.minute:
            return "Classes just ended at " + datetime.datetime.strptime(str(endTime),'%H:%M:%S').strftime('%I:%M %p') + ", so the dining halls might get/be busy now."

        elif currentHour - endTime.hour == 1 and currentMinute < endTime.minute:
            return "Classes just ended at " + datetime.datetime.strptime(str(endTime),'%H:%M:%S').strftime('%I:%M %p') + ", so the dining halls might get/be busy now."
        
        elif endTime.hour >= currentHour and endTime.hour - currentHour <= 1 and (currentMinute >= 30):
            return "Classes will end soon at " + datetime.datetime.strptime(str(endTime),'%H:%M:%S').strftime('%I:%M %p') + ", and the dining halls will get busier."
     
    return "Dining halls are probably not busy at this time."
# ===============

# ===== RESTAURANTS CHECKS =====
'''
Checks whether a restaurant name already exists
'''
def checkRestaurantExists(restaurantName):
    query = "SELECT * FROM restaurants WHERE upper(name) = ?"

    cursor, readConn = setupCursor("read")
    cursor.execute(query, (restaurantName.upper(), ))
    resultSet = cursor.fetchall()
    readConn.close()

    if resultSet == None or not resultSet: return False
    return True

'''
Checks whether a restaurant id is valid
'''
def checkValidRestaurant(restaurantID):
    query = "SELECT * FROM restaurants WHERE id = ?"

    cursor, readConn = setupCursor("read")
    cursor.execute(query, (restaurantID, ))
    resultSet = cursor.fetchall()
    readConn.close()

    if resultSet == None or not resultSet: return False
    return True
# ===============

# ===== RESTAURANT DB CHANGES =====
'''
Updates restaurant information
'''
def updateRestaurantInfo(restaurantID, restaurantName, restaurantAddress):
    query = "UPDATE restaurants SET name = ?, address = ? WHERE id = ?"

    cursor, writeConn = setupCursor("write")
    cursor.execute(query, (restaurantName, restaurantAddress, restaurantID))
    writeConn.commit()
    writeConn.close()

'''
Add restaurant
'''
def insertRestaurant(name, onCampus, address):
    query = "INSERT INTO restaurants (name, on_campus, address) VALUES (?, ?, ?)"

    cursor, writeConn = setupCursor("write")
    cursor.execute(query, (name, onCampus, address))
    writeConn.commit()
    writeConn.close()

'''
Delete restaurant
Deletes attached tags first
'''
def deleteRestaurant(restaurantID):
    clearRestaurantTags(restaurantID)

    query = "DELETE FROM restaurants WHERE id = ?"

    cursor, writeConn = setupCursor("write")
    cursor.execute(query, (restaurantID, ))
    writeConn.commit()
    writeConn.close()
# ===============

# ===== RESTAURANT TAGS =====
'''
Gets all tags associated with a given restaurant
'''
def getRestaurantTags(restaurantID):
    query = "SELECT tag_name FROM restaurantInfo WHERE restaurant_id = ?"

    cursor, readConn = setupCursor("read")
    cursor.execute(query, (restaurantID, ))
    resultSet = cursor.fetchall()
    readConn.close()

    return isolateFirstValueFromTuple(resultSet)

'''
Inserts the tags of specified restaurant
'''
def addRestaurantTags(restaurantID, restaurantTags):
    query = "INSERT IGNORE INTO restaurantInfo (restaurant_id, tag_name) VALUES (?, ?)"

    cursor, writeConn = setupCursor("write")
    for tag in restaurantTags:
        cursor.execute(query, (restaurantID, tag))
    writeConn.commit()
    writeConn.close()

'''
Deletes all tags for the given restaurant
'''
def clearRestaurantTags(restaurantID):
    query = "DELETE FROM restaurantInfo WHERE restaurant_id = ?"

    cursor, deleteConn = setupCursor("write")
    cursor.execute(query, (restaurantID,))
    deleteConn.commit()
    deleteConn.close()
# ===============

# ===== GET RESTAURANT INFO =====
'''
Returns a dictionary of off campus restaurants from database
    KEY == restaurant name
    VALUE == address
'''
def getOffCampusRestaurants():
    query = "SELECT name, id, address FROM restaurants WHERE on_campus = false ORDER BY name, address"

    cursor, readConn = setupCursor("read")
    cursor.execute(query)
    resultSet = cursor.fetchall()
    readConn.close()

    resultDict = dict()
    for restaurant in resultSet:
        resultDict[restaurant[0]] = (restaurant[1], restaurant[2])

    return resultDict

'''
Gets id of requested restaurant name
'''
def getRestaurantID(restaurantName):
    query = "SELECT id FROM restaurants WHERE name = ?"

    cursor, readConn = setupCursor("read")
    cursor.execute(query, (restaurantName,))
    resultSet = cursor.fetchall()
    readConn.close()

    return isolateFirstValueFromTuple(resultSet)[0]

'''
Gets name of requested restaurant id
'''
def getRestaurantName(restaurantID):
    query = "SELECT name FROM restaurants WHERE id = ?"

    cursor, readConn = setupCursor("read")
    cursor.execute(query, (restaurantID,))
    resultSet = cursor.fetchall()
    readConn.close()

    return isolateFirstValueFromTuple(resultSet)[0]

'''
Gets address of requested restaurant id
'''
def getRestaurantAddress(restaurantID):
    query = "SELECT address FROM restaurants WHERE id = ?"

    cursor, readConn = setupCursor("read")
    cursor.execute(query, (restaurantID,))
    resultSet = cursor.fetchall()
    readConn.close()

    return isolateFirstValueFromTuple(resultSet)[0]

'''
Gets restaurants based on selected tags
'''
def getRestaurantsUsingTags(tagIncludeList, tagExcludeList):
    # if empty return all restaurants
    if not bool(tagIncludeList) and not bool(tagExcludeList): return getOffCampusRestaurants()

    fullQuery = ''
    baseQuery = 'SELECT restaurants.name, restaurants.address FROM restaurants INNER JOIN restaurantInfo ON restaurantInfo.restaurant_id = restaurants.id '
    if bool(tagIncludeList):
        includeQuery = baseQuery + "WHERE ("
        whereClause = "tag_name = "
        for _ in tagIncludeList:
            clause = whereClause + "?"
            includeQuery += clause
            whereClause = " OR tag_name = "

        includeQuery += ")" 
        fullQuery += includeQuery
    
    if bool(tagExcludeList):
        excludeQuery = baseQuery + "WHERE ("
        whereClause = "tag_name <> "
        for _ in tagExcludeList:
            clause = whereClause + "?"
            excludeQuery += clause
            whereClause = " AND tag_name <> "

        excludeQuery += ")"
        if bool(tagIncludeList): fullQuery += " INTERSECT " + excludeQuery
        else: fullQuery += excludeQuery

    combinedTagLists = tagIncludeList + tagExcludeList
    cursor, readConn = setupCursor("read")
    cursor.execute(fullQuery, combinedTagLists)
    resultSet = cursor.fetchall()
    readConn.close()

    resultDict = {}
    for restaurant in resultSet:
        resultDict[restaurant[0]] = restaurant[1]

    return resultDict
# ===============
