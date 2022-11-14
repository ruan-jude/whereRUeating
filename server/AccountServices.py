import bcrypt, re
from server.DatabaseServices import setup_cursor, isolate_first_value_from_tuple

'''
Checks whether account exists
    If exists, return True and (id, username, password)
    Else, returns False and error msg
FUNCTIONING
'''
def authenticate_account(username_input, password_input):
    cursor,read_conn = setup_cursor("read")
    cursor.execute("SELECT * FROM users WHERE username=?", (username_input,))
    result_set = cursor.fetchall()

    if result_set==None or not result_set: 
        read_conn.close()
        return False, "User does not exist"

    retrieved_hash = result_set[0][3]
    password_matches = bcrypt.checkpw(password_input.encode('utf-8'), retrieved_hash.encode('utf-8'))
    read_conn.close()

    if password_matches:
        return True, result_set[0]
    else:
        return False, 'Incorrect login'

'''
Checks whether inputed account info is valid
    If exists, return True and success msg
    Else, return False and error msg
FUNCTIONING
'''
def create_account(email_input, username_input, password_input, confirm_input):
    cursor,write_conn = setup_cursor("write")

    # database call that searches if someone already has that login
    cursor.execute("SELECT email FROM users WHERE email=?", (email_input,))
    if cursor.rowcount != 0:
        write_conn.close()
        return False, 'Account with that email already exists!'

    check_input = sanitize_info(email_input, username_input, password_input)
    if check_input != True:
        write_conn.close()
        return check_input

    # checks if the passwords match, if not return error msg
    if password_input != confirm_input:
        write_conn.close()
        return False, 'Passwords do not match!'

    # hashes the password
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password_input.encode('utf-8'), salt)

    # inserts into the database
    cursor.execute("INSERT INTO users (email, username, password) VALUES (?,?,?)", (email_input, username_input, hash))
    write_conn.commit()
    write_conn.close()

    # gets the information for the user
    cursor,read_conn = setup_cursor("read")
    cursor.execute("SELECT * FROM users WHERE username=?", (username_input,))
    result_set = cursor.fetchall()
    read_conn.close()
    return True, result_set[0]

'''
Checks validity of email, username, and password inputed
FUNCTIONING
'''
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
    elif not username_input or not password_input or not email_input:
        return False, 'Please fill out the form!'

    return True

'''
User preferences for include and diet are obtained directly from HTML and combined
FUNCTIONING
'''
def synthesize_whitelist(include_list, diet_list):
    full_include_list = include_list + diet_list
    return full_include_list

'''
Inserts the whitelist and blacklist into userPreferences table
FUNCTIONING
'''
def add_user_preferences(current_user_id, whitelist, blacklist):
    cursor,write_conn = setup_cursor("write")

    for tag in whitelist:
        cursor.execute("INSERT IGNORE INTO userPreferences (user_id, tag_name, exclude) VALUES (?, ?, ?)", (current_user_id, tag, 0))

    for tag in blacklist:
        cursor.execute("INSERT IGNORE INTO userPreferences (user_id, tag_name, exclude) VALUES (?, ?, ?)", (current_user_id, tag, 1))

    write_conn.commit()
    write_conn.close()

'''
Returns the whitelist (where exclude = 0)  and the blacklist (where exclude = 1) of the specified user
FUNCTIONING
'''
def get_user_preferences(current_user_id):
    cursor, read_conn = setup_cursor("read")
    
    # whitelist query
    cursor.execute("SELECT tag_name FROM userPreferences WHERE exclude = false AND user_id = ?", (current_user_id,))
    whitelist_result_set = cursor.fetchall()

    # blacklist query
    cursor.execute("SELECT tag_name FROM userPreferences WHERE exclude = true AND user_id = ?", (current_user_id,))
    blacklist_result_set = cursor.fetchall()

    read_conn.close()
    return isolate_tag_names(whitelist_result_set, blacklist_result_set)

'''
Deletes preferences of specified user
FUNCTIONING
'''
def clear_user_preferences(current_user_id):
    cursor, delete_conn = setup_cursor("user_preferences")
    cursor.execute("DELETE FROM userPreferences WHERE user_id = ?", (current_user_id,))
    delete_conn.commit()
    delete_conn.close()

def delete_user_preference(current_user_id):
    cursor,write_conn = setup_cursor("write")
    cursor.execute("DELETE FROM userPreferences WHERE user_id = ?", (current_user_id,))
    write_conn.commit()
    return True, "Preferences cleared!"

'''
Isolates tags from all other information
FUNCTIONING
'''
def isolate_tag_names(whitelist_result_set, blacklist_result_set):
    return isolate_first_value_from_tuple(whitelist_result_set), isolate_first_value_from_tuple(blacklist_result_set)
