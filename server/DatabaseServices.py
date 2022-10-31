import mariadb

def setup_cursor(mode):
    db_user = "root"
    db_pwd = "VARRC"
   
    if mode == "read":
        db_user = "root"
        db_pwd = "VARRC"
    elif mode == "write":
        db_user = "root"
        db_pwd = "VARRC"
    
    try:
        conn = mariadb.connect(
            user = db_user,
            password = db_pwd,
            #host="",
            port = 3306,
            database = "whereRUeating"
        )
        conn.autocommit = False
        
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
    
    cursor = conn.cursor()
    return cursor,conn    


if __name__ == "__main__":
    main()
