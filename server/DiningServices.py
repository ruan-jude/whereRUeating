import datetime
from server.HelperMethods import *
from server.DatabaseServices import *

BUSY_CLASS_END_TIMES = [datetime.time(11,40,0), datetime.time(13,20, 0), datetime.time(15,20,0), datetime.time(18,0,0)]

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
     
    return "Probably not busy at this time."

'''
Returns a dictionary of off campus restaurants from database
    KEY == restaurant name
    VALUE == address
'''
def getOffCampusRestaurants():
    query = "SELECT name, address FROM restaurants WHERE on_campus = false ORDER BY name, address"

    cursor, readConn = setupCursor("read")
    cursor.execute(query)
    resultSet = cursor.fetchall()
    readConn.close()

    resultDict = dict()
    for restaurant in resultSet:
        resultDict[restaurant[0]] = restaurant[1]

    return resultDict

'''
Gets id of requested restaurant name
'''
def getRestaurantId(restaurantName):
    query = "SELECT id FROM restaurants WHERE name = restaurantName"

    cursor, readConn = setupCursor("read")
    cursor.execute(query)
    resultSet = cursor.fetchall()
    readConn.close()

    print(resultSet)

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
