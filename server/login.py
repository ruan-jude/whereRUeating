import bcrypt
import sys
import mariadb

#i have no idea if any of this works

def setup_cursor(mode):
    db_user = ""
    db_pwd = ""
   
    if mode == "read":
        db_user = ""
        db_pwd = ""
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
    if mode == "write":
        return cursor,conn
    else:
        return cursor

#THIS FUNCTION CURRENTLY DOES NOT WORK
def verify_password(username_input, password_input):
    cursor = setup_cursor("read")
    print(username_input)
    print(cursor)
    cursor.execute("SELECT * FROM users")
    result_set = cursor.fetchall()  
 # result_set = cursor.execute("SELECT password FROM users WHERE username=?", (username_input,))

    if result_set == None:
        print("invalid_login: user does not exist")
        return

    print(result_set)
    retrieved_hash = result_set.first[0]
    retrieved_salt = retrieved_hash[7:29] #.decode('utf-8')
    password_hash = retrieved_hash[29:]
    
    new_hash = bcrypt.hashpw(password_input.encode('utf-8'), retrieved_salt)
    if retrieved_hash == new_hash:
        print('Valid login')
    else:
        print('incorrect login')
         
def create_account(email_input, username_input, password_input):
    cursor,write_conn = setup_cursor("write")
    cursor.execute("SELECT email FROM users WHERE email=?", (email_input,))#database call that searches if someone already has that login
    if cursor.rowcount != 0:
        print('account with that email already exists')
        
    sanitize_info(email_input, username_input)
    
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password_input.encode('utf-8'), salt)
    
    cursor.execute("INSERT INTO users (email, username, password) VALUES (?,?,?)", (email_input, username_input, hash))
    #cursor.commit()
    write_conn.commit()
    
def sanitize_info(email_input, username_input):
    #check length
    #check for disallowed characters
    print("will finish this later")


def main():
    create_account("testemail@gmail.com", "testUser", "testpassword")
    #verify_password("testUser", "testpassword") 

if __name__ == "__main__":
    main()


