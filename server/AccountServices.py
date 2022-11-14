import bcrypt
import re
from DatabaseServices import setup_cursor, isolate_first_value_from_tuple

def authenticate_account(username_input, password_input):
    cursor,read_conn = setup_cursor("read")
    cursor.execute("SELECT * FROM users WHERE username=?", (username_input,))
    result_set = cursor.fetchall()

    if result_set==None or not result_set: 
        return False, "Invalid login: user does not exist"
    retrieved_hash = result_set[0][3]

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
        return 'Account with that email already exists!'

    check_input = sanitize_info(email_input, username_input, password_input)

    if check_input != "Valid input":
        return check_input

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

# Should probably make sure everything is alphanumeric or an allowed special char here
def sanitize_info(email_input, username_input, password_input):
    #check length
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
    return "Valid input"

def getUserId(current_user):
    cursor, read_conn = setup_cursor("read")
    baseQuery = "SELECT id FROM users WHERE username = ?"
    cursor.execute(baseQuery, (current_user,))
    result_set = cursor.fetchall()

    if not result_set: #or if result set is greater than 1
        return None

    read_conn.close()
    return result_set[0][0]

def synthesize_whitelist(include_list, diet_list):
    full_include_list = include_list + diet_list
    return full_include_list

def add_user_preferences(current_user, whitelist, blacklist):
    cursor,write_conn = setup_cursor("write")
    whitelist_query = "INSERT IGNORE INTO userPreferences (user_id, tag_name, exclude) VALUES (?, ?, ?)"
    blacklist_query = "INSERT IGNORE INTO userPreferences (user_id, tag_name, exclude) VALUES (?, ?, ?)"

    user_id = getUserId(current_user)

    if user_id is None:
        return "ERROR: User does not exist"

    for tag in whitelist:
        cursor.execute(whitelist_query, (user_id, tag, 0))

    for tag in blacklist:
        cursor.execute(blacklist_query, (user_id, tag, 1))

    write_conn.commit()
    write_conn.close()

    return "Preferences updated!"

def get_user_preferences(current_user):
    cursor, read_conn = setup_cursor("read")
    whitelistQuery = "SELECT tag_name FROM userPreferences WHERE exclude = false AND user_id = ?"
    blacklistQuery = "SELECT tag_name FROM userPreferences WHERE exclude = true AND user_id = ?"
    
    retrieved_id = getUserId(current_user)
    if not retrieved_id:
        return None

    cursor.execute(whitelistQuery, (retrieved_id,))
    whitelist_result_set = cursor.fetchall()

    cursor.execute(blacklistQuery, (retrieved_id,))
    blacklist_result_set = cursor.fetchall()

    read_conn.close()
    return isolate_tag_names(whitelist_result_set, blacklist_result_set)

def clear_user_preferences(current_user):
    cursor, delete_conn = setup_cursor("user_preferences")
    baseQuery = "DELETE FROM userPreferences WHERE user_id = ?"

    retrieved_id = getUserId(current_user)
    if not retrieved_id:
        return None

    cursor.execute(baseQuery, (retrieved_id,))
    delete_conn.commit()
    delete_conn.close()

def delete_user_preference(current_user):
    cursor,write_conn = setup_cursor("write")
    delete_query = "DELETE FROM userPreferences WHERE user_id = ?"

    retrieved_id = getUserId(current_user)
    if not retrieved_id:
        return False, "Invalid user"

    cursor.execute(delete_query, (retrieved_id,))
    write_conn.commit()
    return True, "Preferences cleared!"


def isolate_tag_names(whitelist_result_set, blacklist_result_set):
    return isolate_first_value_from_tuple(whitelist_result_set), isolate_first_value_from_tuple(blacklist_result_set)

def main():
    # create_account("testemail@gmail.com", "testUser", "testpassword")
    print("hi")
    print(authenticate_account("testUser", "testpassword"))

if __name__ == "__main__":
    main()

