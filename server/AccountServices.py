import bcrypt, re
from server.HelperMethods import *
from server.DatabaseServices import *

# ===== ACCOUNT CREATION =====
'''
Checks whether account exists
    If exists, return True and (id, username, password)
    Else, returns False and error msg
'''
def authenticateAccount(usernameInput, passwordInput):
    query = "SELECT * FROM users WHERE username=?"

    cursor, readConn = setupCursor("read")
    cursor.execute(query , (usernameInput,))
    resultSet = cursor.fetchall()
    readConn.close()

    # checks if user exists
    if resultSet == None or not resultSet: return False, "User does not exist"

    # checks if passwords match
    retrievedHash = resultSet[0][3]
    passwordMatches = bcrypt.checkpw(passwordInput.encode('utf-8'), retrievedHash.encode('utf-8'))

    if passwordMatches: return True, resultSet[0]
    return False, 'Incorrect login'

'''
Checks whether inputed account info is valid
    If exists, return True and success msg
    Else, return False and error msg
'''
def createAccount(emailInput, usernameInput, passwordInput, confirmInput):
    query1 = "SELECT email FROM users WHERE email=?"
    cursor, readConn = setupCursor("read")
    cursor.execute(query1, (emailInput,))
    rowCount = cursor.rowcount
    readConn.close()

    # == Account validity check ==
    if rowCount != 0: return False, 'Account with that email already exists!'

    checkInput = sanitizeInfo(emailInput, usernameInput, passwordInput)
    if checkInput != True: return checkInput

    if passwordInput != confirmInput: return False, 'Passwords do not match!'
    # =====

    # hashes the password
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(passwordInput.encode('utf-8'), salt)

    # inserts user information into database
    query2 = "INSERT INTO users (email, username, password) VALUES (?,?,?)"
    cursor, writeConn = setupCursor("write")
    cursor.execute(query2, (emailInput, usernameInput, hash))
    writeConn.commit()
    writeConn.close()

    # gets the id and username of the new user
    query3 = "SELECT * FROM users WHERE username=?"
    cursor,readConn = setupCursor("read")
    cursor.execute(query3, (usernameInput,))
    resultSet = cursor.fetchall()
    readConn.close()

    # adding user role to new user in userRoles table
    query4 = "INSERT INTO userRoles (user_id, role_id) VALUES (?, ?)"
    cursor,write_conn = setupCursor("write")
    cursor.execute(query4, (resultSet[0][0], 3))
    write_conn.commit()
    write_conn.close()
    
    return True, resultSet[0]

'''
Checks validity of email, username, and password inputed
'''
def sanitizeInfo(emailInput, usernameInput, passwordInput):
    if len(emailInput) > 128:
        return False, "Email too long"
    elif len(usernameInput) > 32:
        return False, "Username too long"
    elif len(passwordInput) < 8:
        return False, "Password cannot be less than 8 characters long"

    if not re.match(r'[^@]+@[^@]+\.[^@]+', emailInput):
        return False, 'Invalid email address!'
    elif not re.match(r'[A-Za-z0-9]+', usernameInput):
        return False, 'Username must contain only characters and numbers!'
    elif not usernameInput or not passwordInput or not emailInput:
        return False, 'Please fill out the form!'

    return True
# ===============

# ===== USER PREFERENCES =====
'''
Inserts the whitelist and blacklist into userPreferences table
'''
def addUserPreferences(currUserID, whitelist, blacklist):
    cursor, writeConn = setupCursor("write")

    whitelistQuery = "INSERT IGNORE INTO userPreferences (user_id, tag_name, exclude) VALUES (?, ?, ?)"
    for tag in whitelist:
        cursor.execute(whitelistQuery, (currUserID, tag, 0))

    blacklistQuery = "INSERT IGNORE INTO userPreferences (user_id, tag_name, exclude) VALUES (?, ?, ?)"
    for tag in blacklist:
        cursor.execute(blacklistQuery, (currUserID, tag, 1))

    writeConn.commit()
    writeConn.close()

'''
Returns the whitelist (where exclude = 0)  and the blacklist (where exclude = 1) of the specified user
'''
def getUserPreferences(currUserID):
    cursor, readConn = setupCursor("read")
    
    whitelistQuery = "SELECT tag_name FROM userPreferences WHERE exclude = false AND user_id = ?"
    cursor.execute(whitelistQuery, (currUserID,))
    whitelistResultSet = cursor.fetchall()

    blacklistQuery = "SELECT tag_name FROM userPreferences WHERE exclude = true AND user_id = ?"
    cursor.execute(blacklistQuery, (currUserID,))
    blacklistResultSet = cursor.fetchall()

    readConn.close()
    return isolateTagNames(whitelistResultSet, blacklistResultSet)

'''
Deletes preferences of specified user
'''
def clearUserPreferences(currUserID):
    query = "DELETE FROM userPreferences WHERE user_id = ?"

    cursor, deleteConn = setupCursor("userPreferences")
    cursor.execute(query, (currUserID,))
    deleteConn.commit()
    deleteConn.close()
# ==========

# ===== USER FAVORITES =====
'''
Clear favorites of specified user
'''
def clearUserFavs(userID):
    query = "DELETE FROM userFavs WHERE user_id=?"

    cursor, deleteConn = setupCursor("write")
    cursor.execute(query, (userID,))
    deleteConn.commit()
    deleteConn.close()

'''
Returns the list of dish ids in the favorites list
'''
def getUserFavs(userID):
    query = "SELECT dish_id FROM userFavs WHERE user_id = ?"

    cursor, readConn = setupCursor("read")
    cursor.execute(query, (userID,))
    favDishes = cursor.fetchall()
    readConn.close()

    return isolateFirstValueFromTuple(favDishes)

'''
Inserts the whitelist and blacklist into userPreferences table
'''
def addUserFavs(userID, favDishes):
    query = "INSERT IGNORE INTO userFavs (user_id, dish_id) VALUES (?, ?)"
    
    cursor, writeConn = setupCursor("write")
    for dishIDs in favDishes:
        cursor.execute(query, (userID, dishIDs))
    writeConn.commit()
    writeConn.close()

# ==============

# ===== GENERAL USERS =====
'''
Gets user ids and usernames
'''
def getAllUsers():
    query = "SELECT id, username FROM users"

    cursor, readConn = setupCursor("read")
    cursor.execute(query)
    users = cursor.fetchall()
    readConn.close()

    return users
    
'''
Gets user role id
'''
def getUserRole(userID):
    query = "SELECT role_id FROM userRoles WHERE user_id = ?"

    cursor, readConn = setupCursor("read")
    cursor.execute(query, (userID,))
    userRole = cursor.fetchall()
    readConn.close()

    return userRole[0][0]

'''
Checks whether a user id is valid
'''
def validUser(userID):
    query = "SELECT * FROM users WHERE id = ?"

    cursor, readConn = setupCursor("read")
    cursor.execute(query, (userID, ))
    resultSet = cursor.fetchall()
    readConn.close()

    if resultSet == None or not resultSet: return False
    return True

'''
Get username attached to user_id
'''
def getUsername(userID):
    query = "SELECT username FROM users WHERE id = ?"

    cursor, readConn = setupCursor("read")
    cursor.execute(query, (userID, ))
    resultSet = cursor.fetchall()
    readConn.close()

    return resultSet[0][0]
# ==============