import mariadb
import server.ServerConstants as ServerConstants

def setup_cursor(mode):
    db_user = ""
    db_pwd = ""
   
    if mode == "read":
        db_user = ServerConstants.READER_USERNAME
        db_pwd = ServerConstants.READER_PASSWORD
    elif mode == "write":
        db_user = ServerConstants.WRITER_USERNAME
        db_pwd = ServerConstants.WRITER_PASSWORD
    elif mode == "test":
        db_user = ServerConstants.TESTING_USERNAME
        db_pwd = ServerConstants.TESTING_PASSWORD
    elif mode == "user_preferences":
        db_user = ServerConstants.USER_PREFERENCE_USERNAME
        db_pwd = ServerConstants.USER_PREFERENCE_PASSWORD
    
    try:
        conn = mariadb.connect(
            user = db_user,
            password = db_pwd,
            port = 3306,
            database = "whereRUeating"
            #database = "testDB"
        )
        conn.autocommit = False

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
    
    cursor = conn.cursor()
    return cursor,conn    

def isolate_first_value_from_tuple(result_set):
    isolated_set = []

    for result_tuple in result_set:
        isolated_set.append(result_tuple[0])

    return isolated_set
