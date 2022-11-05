import mariadb
from DatabaseServices import setup_cursor

def getMenuItems(requested_date, restaurant_name):
    cursor, read_conn = setup_cursor("read")
    cursor.execute("SELECT menuItems.dish_id, dishes.name FROM menuItems  INNER JOIN dishes ON menuItems.dish_id = dishes.id WHERE menuItems.restaurant_id = 1 AND menuItems.date = ?;", (requested_date,))
    result_set = cursor.fetchall() 

    print(result_set)
    for row in result_set:
        print(row)

    read_conn.close()
    return result_set

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

def selectMenuItemsWithUserPreferences(whitelist, blacklist, dining_hall):
    if not whitelist and blacklist:
        return selectMenuItemsExcludingTags(blacklist, dining_hall)
    elif whitelist and not blacklist:
        return selectMenuItemsIncludingTags(whitelist, dining_hall)

    
    print("does something")
    
def selectMenuItemsIncludingTags(tagList, dining_hall):
    baseQuery = "SELECT menuItems.dish_id, dishes.name, dishInfo.tag_name FROM menuItems INNER JOIN dishInfo ON menuItems.dish_id = dishInfo.dish_id INNER JOIN dishes ON menuItems.dish_id = dishes.id"
    whereClause = " WHERE dishInfo.tag_name = ?"
    cursor, read_conn = setup_cursor("read")

    if dining_hall:
        baseQuery = baseQuery + " WHERE menuItems.restaurant_id = " + dining_hall
        whereClause = " AND (dishInfo.tag_name = ?"

    for tag in tagList:
        #print(tag)
        baseQuery = baseQuery + whereClause
        if tagList.index(tag) == 0:
            whereClause = " OR dishInfo.tag_name = ?" 

    if dining_hall:
        baseQuery = baseQuery + ")"

    #print(baseQuery)
    cursor.execute(baseQuery, tagList)
    result_set = cursor.fetchall()
    print(result_set)
    read_conn.close()
    return result_set

def selectMenuItemsExcludingTags(tagList, dining_hall):
    baseQuery = "SELECT menuItems.dish_id, dishes.name, dishInfo.tag_name FROM menuItems INNER JOIN dishInfo ON menuItems.dish_id = dishInfo.dish_id INNER JOIN dishes ON menuItems.dish_id = dishes.id"
    whereClause = " WHERE dishInfo.tag_name = ?"
    cursor, read_conn = setup_cursor("read")

    if dining_hall:
        baseQuery = baseQuery + " WHERE menuItems.restaurant_id = " + dining_hall
        whereClause = " AND (dishInfo.tag_name = ?"

    for tag in tagList:
        #print(tag)
        baseQuery = baseQuery + whereClause
        if tagList.index(tag) == 0:
            whereClause = " OR dishInfo.tag_name = ?" 

    if dining_hall:
        baseQuery = baseQuery + ")"

    #print(baseQuery)
    cursor.execute(baseQuery, tagList)
    result_set = cursor.fetchall()
    print(result_set)
    read_conn.close()
    return result_set

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