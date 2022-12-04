import mariadb
import server.ServerConstants as ServerConstants

'''
Creates a connection to the database
FUNCTIONING
'''
def setupCursor(mode):
    dbUser = ""
    dbPwd = ""
   
    if mode == "read":
        dbUser = ServerConstants.READER_USERNAME
        dbPwd = ServerConstants.READER_PASSWORD
    elif mode == "write":
        dbUser = ServerConstants.WRITER_USERNAME
        dbPwd = ServerConstants.WRITER_PASSWORD
    elif mode == "test":
        dbUser = ServerConstants.TESTING_USERNAME
        dbPwd = ServerConstants.TESTING_PASSWORD
    elif mode == "userPreferences":
        dbUser = ServerConstants.USER_PREFERENCE_USERNAME
        dbPwd = ServerConstants.USER_PREFERENCE_PASSWORD
    
    try:
        conn = mariadb.connect(
            user = dbUser,
            password = dbPwd,
            port = 3306,
            database = "whereRUeating"
        )
        conn.autocommit = False

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
    
    cursor = conn.cursor()
    return cursor, conn    

