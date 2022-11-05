import bcrypt
import sys
import mariadb
import re
from .DatabaseServices import setup_cursor

# ===== WORKING =====
def authenticate_account(username_input, password_input):
    cursor,read_conn = setup_cursor("read")
    cursor.execute("SELECT * FROM users WHERE username=?", (username_input,))
    result_set = cursor.fetchall()

    if result_set==None or not result_set: 
        return False, "Invalid login: user does not exist"
    retrieved_hash = result_set[0][3]
    retrieved_salt = retrieved_hash[7:29] #.decode('utf-8')
    password_hash = retrieved_hash[29:]

    password_matches = bcrypt.checkpw(password_input.encode('utf-8'), retrieved_hash.encode('utf-8'))
    read_conn.close()

    if password_matches:
        return True, result_set[0]
    else:
        return False, 'Incorrect login'

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

    passed, msg = sanitize_info(email_input, username_input, password_input)
    if not passed: return msg

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
    if len(email_input) > 128:
        return False, "Email too long"
    elif len(username_input) > 32:
        return False, "Username too long"
    elif len(password_input) < 8:
        return False, "Password cannot be less than 8 characters long"
    
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email_input):
        return False, 'Invalid email address!'
    elif not re.match(r'[A-Za-z0-9]+', username_input):
        return False, 'Username must contain only characters and numbers!'
    elif not username or not password or not email:
        return False, 'Please fill out the form!'
    
    return True, None

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



