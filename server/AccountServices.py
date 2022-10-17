import bcrypt
import sys
import mariadb

def setup_cursor(mode):
    db_user = "root"
    db_pwd = ""

    if mode == "read":
        db_user = "db_reader"
        db_pwd = "prometheus2007"
    elif mode == "write":
        db_user = "db_writer"
        db_pwd = "deaconblackfire1988"

    try:
        conn = mariadb.connect(
                user = db_user,
                password = db_pwd,
                port = 3306,
                database = "whereRUeating"
                )
        conn.autocommit = False

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")

    cursor = conn.cursor()
    return cursor,conn


# ===== WORKING =====
def verify_password(username_input, password_input):
    cursor,read_conn = setup_cursor("read")
    cursor.execute("SELECT password FROM users WHERE username=?", (username_input,))
    result_set = cursor.fetchall()

    if result_set==None or not result_set: return "Invalid login: user does not exist"

    retrieved_hash = result_set[0][0]
    retrieved_salt = retrieved_hash[7:29] #.decode('utf-8')
    password_hash = retrieved_hash[29:]

    password_matches = bcrypt.checkpw(password_input.encode('utf-8'), retrieved_hash.encode('utf-8'))
    read_conn.close()
    if password_matches:
        return 'Valid login'
    else:
        return 'Incorrect login'

def create_account(email_input, username_input, password_input, confirm_input):
    cursor,write_conn = setup_cursor("write")

    # database call that searches if someone already has that login
    cursor.execute("SELECT email FROM users WHERE email=?", (email_input,))
    if cursor.rowcount != 0:
        return 'Account with that email already exists!'

    sanitize_info(email_input, username_input, password_input)

    # checks if the passwords match, if not return error msg
    if password_input != confirm_input:
        return 'Passwords do not match!'

    # hashes the password
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password_input.encode('utf-8'), salt)

    # inserts into the database
    cursor.execute("INSERT INTO users (email, username, password) VALUES (?,?,?)", (email_input, username_input, hash))
    write_conn.commit()
    write_conn.close()
    return 'Created user or something'

def sanitize_info(email_input, username_input, password_input):
    #check length
    #check for disallowed characters
    # print("will finish this later")
    pass


#def main():
#create_account("testemail@gmail.com", "testUser", "testpassword")
#verify_password("testUser", "testpassword")



