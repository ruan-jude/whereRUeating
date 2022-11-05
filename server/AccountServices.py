import bcrypt
from server.DatabaseServices import setup_cursor

# ===== WORKING =====
def verify_password(username_input, password_input):
    cursor,read_conn = setup_cursor("read")
    cursor.execute("SELECT password FROM users WHERE username=?", (username_input,))
    result_set = cursor.fetchall()

    if result_set==None or not result_set: return "Invalid login: user does not exist"

    retrieved_hash = result_set[0][0]

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

    disallowed_characters = ['\0', '\n', '--']
    for dis_char in disallowed_characters:
        if dis_char in password_input:
            return "Password contains disallowed character"
        
    return "Valid input"

def getUserId(current_user):
    cursor, read_conn = setup_cursor("read")
    baseQuery = "SELECT id FROM users WHERE username = ?"
    cursor.execute(baseQuery, (current_user,))
    result_set = cursor.fetchall()

    if not result_set: #or if result set is greater than 1
        return None
    
    read_conn.close()
    return result_set[0]

def add_user_preference(current_user, tagList):
    cursor,write_conn = setup_cursor("write")
    baseQuery = "INSERT INTO userPreferences (user_id, tag_name, exclude) VALUES (?, ?, ?)"

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
    print(whitelist_result_set)
    print()
    print(blacklist_result_set)
    return whitelist_result_set, blacklist_result_set

def main():
    # create_account("testemail@gmail.com", "testUser", "testpassword")
    print("hi")
    print(verify_password("testUser", "testpassword"))

if __name__ == "__main__":
    main()

