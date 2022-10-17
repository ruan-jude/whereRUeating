import mariadb

def setup_cursor(mode):
    db_user = ""
    db_pwd = ""
   
    if mode == "read":
        db_user = ""
        db_pwd = ""
    elif mode == "write":
        db_user = ""
        db_pwd = ""
    
    try:
        conn = mariadb.connect(
            user = db_user,
            password = db_pwd,
            #host="",
            port = 3306,
            database = "testDB"
        )
        conn.autocommit = False
        
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
    
    cursor = conn.cursor()
    return cursor,conn

def getMenuItems(requested_date, restaurant_name):

    cursor, read_conn = setup_cursor("read")
    rd = "2022-10-18"
    cursor.execute("SELECT menuItems.dish_id, dishes.name FROM menuItems  INNER JOIN dishes ON menuItems.dish_id = dishes.id WHERE menuItems.restaurant_id = 1 AND menuItems.date = ?;", (rd,))
    result_set = cursor.fetchall() 

    for row in result_set:
        print(row)

    read_conn.close()


def main():
    getMenuItems("something", "restaurant_name")

if __name__ == "__main__":
    main()