import mariadb

def setup_cursor(mode):
    db_user = ""
    db_pwd = ""
   
    if mode == "read":
        db_user = ""
        db_pwd = ""
        print("establishing read connection with db reader")
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


def main():
    print("Running db_services.py")

if __name__ == "__main__":
    main()
