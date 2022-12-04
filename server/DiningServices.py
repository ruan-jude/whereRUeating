import datetime, sys
sys.path.append("/home/cch106/whereRUeating-main")
from server.DatabaseServices import setup_cursor

busy_class_end_times = [datetime.time(11,40,0), datetime.time(13,20, 0), datetime.time(15,20,0), datetime.time(18,0,0)]

def check_dining_halls_busy():
    current_time = datetime.datetime.now()
    current_minute = current_time.minute
    current_hour = current_time.hour

    for end_time in busy_class_end_times:

        if (current_hour - end_time.hour) == 0 and current_minute >= end_time.minute:
            return "Classes just ended at " + datetime.datetime.strptime(str(end_time),'%H:%M:%S').strftime('%I:%M %p') + ", so the dining halls might get/be busy now."

        elif current_hour - end_time.hour == 1 and current_minute < end_time.minute:
            return "Classes just ended at " + datetime.datetime.strptime(str(end_time),'%H:%M:%S').strftime('%I:%M %p') + ", so the dining halls might get/be busy now."
        
        elif end_time.hour >= current_hour and end_time.hour - current_hour <= 1 and (current_minute >= 30):
            return "Classes will end soon at " + datetime.datetime.strptime(str(end_time),'%H:%M:%S').strftime('%I:%M %p') + ", and the dining halls will get busier."
     
    return "Probably not busy at this time."

# returns a dictionary of off campus restaurants from database
# dictionary uses the restuarant name as the KEY, and the address as the VALUE
def getOffCampusRestaurants():
    cursor, read_conn = setup_cursor("read")
    cursor.execute("SELECT name, address FROM restaurants WHERE on_campus = false ORDER BY name, address")
    result_set = cursor.fetchall()
    result_dict = {}
    for restaurant in result_set:
        result_dict[restaurant[0]] = restaurant[1]

    # for key in result_dict:
    #     print(key + ": " + result_dict[key])

    read_conn.close()

    return result_dict

def getRestaurantsUsingTags(tag_include_list, tag_exclude_list):
    if len(tag_include_list) == 0 and len(tag_exclude_list) == 0:
        return getOffCampusRestaurants()

    cursor, read_conn = setup_cursor("read")

    combined_tag_lists = tag_include_list + tag_exclude_list

    base_query = """SELECT restaurants.name, restaurants.address 
        FROM restaurants INNER JOIN restaurantInfo ON restaurantInfo.restaurant_id = restaurants.id 
        """

    full_query = ""
    
    if len(tag_include_list) != 0:
        include_query = base_query + "WHERE ("
        where_clause = "tag_name = "
        for tag in tag_include_list:
            clause = where_clause + "?"
            include_query = include_query + clause
            where_clause = " OR tag_name = "

        include_query += ")" 
        full_query += include_query

    if len(tag_exclude_list) != 0:
        exclude_query = base_query + "WHERE ("
        where_clause = "tag_name <> "
        for tag in tag_exclude_list:
            clause = where_clause + "?"
            exclude_query = exclude_query + clause
            where_clause = " AND tag_name <> "

        exclude_query += ")"
        if len(tag_include_list) != 0: 
            full_query += " INTERSECT " + exclude_query
        else:
            full_query += exclude_query
            
    # elif len(tag_exclude_list) != 0 :
    #     exclude_query = base_query + "WHERE ("
    #     where_clause = "tag_name <> "
    #     for tag in tag_exclude_list:
    #         clause = where_clause + "?"
    #         exclude_query = exclude_query + clause
    #         where_clause = " AND tag_name <> "

    #     exclude_query += ")" 
    #     full_query += exclude_query

    # print(include_query)
    # print()
    # print(exclude_query)
    # print()
    print(full_query)

    cursor.execute(full_query, combined_tag_lists)

    result_set = cursor.fetchall()
    result_dict = {}
    for restaurant in result_set:
        result_dict[restaurant[0]] = restaurant[1]

    read_conn.close()

    return result_dict

def check_for_events():
    print("doing something now")

if __name__ == '__main__':
    # get_off_campus_restaurants()
    # print(get_off_campus_restaurants())
    # print()
    # print(check_dining_halls_busy())
    print(getRestaurantsUsingTags(("mexican", "mediterranean", "indian"), ("asasdf", "poiupoqwert")))

    

