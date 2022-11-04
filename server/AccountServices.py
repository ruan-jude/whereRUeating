import bcrypt
import sys
import mariadb
from .DatabaseServices import setup_cursor

# ===== WORKING =====
def authenticate_account(username_input, password_input):
    cursor,read_conn = setup_cursor("read")
    cursor.execute("SELECT password FROM users WHERE username=?", (username_input,))
    result_set = cursor.fetchall()

    if result_set==None or not result_set: 
        return "Invalid login: user does not exist"

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
        # return False
        return 'Account with that email already exists!'

    sanitize_info(email_input, username_input, password_input)

    # checks if the passwords match, if not return error msg
    if password_input != confirm_input:
        # return False
        return 'Passwords do not match!'

    # hashes the password
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password_input.encode('utf-8'), salt)

    # inserts into the database
    cursor.execute("INSERT INTO users (email, username, password) VALUES (?,?,?)", (email_input, username_input, hash))
    write_conn.commit()
    write_conn.close()

    # return True
    return 'Created user or something'

def login_account(email_input, username_input, password_input, confirm_input):
    cursor,write_conn = setup_cursor("write")

    # database call that searches if someone already has that login
    cursor.execute("SELECT email FROM users WHERE email=?", (email_input,))
    if cursor.rowcount != 0: 
        # return False
        return 'Account with that email already exists!'

    sanitize_info(email_input, username_input, password_input)

    # checks if the passwords match, if not return error msg
    if password_input != confirm_input:
        # return False
        return 'Passwords do not match!'

    # hashes the password
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password_input.encode('utf-8'), salt)

    # inserts into the database
    cursor.execute("INSERT INTO users (email, username, password) VALUES (?,?,?)", (email_input, username_input, hash))
    write_conn.commit()
    write_conn.close()

    # return True
    return 'Created user or something'

def sanitize_info(email_input, username_input, password_input):
    #check length
    #check for disallowed characters
    #print("will finish this later")
    pass

def add_user_preference(current_user, tagList):
    cursor,write_conn = setup_cursor("write")
    baseQuery = ("INSERT INTO userPreferences (user_id, tag_name) VALUES (?, ?)")

    cursor.execute("SELECT id FROM users WHERE username = ?", (current_user,))
    result_set = cursor.fetchall()

    if not result_set:
        return "ERROR: User does not exist"

    print(result_set[0])
    user_id = result_set[0]

    for tag in tagList:
        cursor.execute(baseQuery, (user_id, tag))

    write_conn.commit()
    write_conn.close()

    return "Preferences updated!"



