import os
import sys
print("SYSTEM PATH: " + str(sys.path))

from server.HelperMethods import *
from server.AccountServices import *
from server.DishServices import *
from server.DiningServices import *
from flask import Flask, render_template, request, redirect, url_for, flash, session

template_dir = os.getcwd() + '/client/'
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'SECRET_KEY'

# ===== HOME PAGES =====
@app.route('/', methods=['GET'])
def home():
    # if user is logged in, go to user home page
    if 'loggedin' in session:
        return redirect(url_for("userHome", username=session['username']))
    
    # else, go to generic home page
    return render_template('Home.html', username="", data="")

@app.route('/Home/<username>/', methods=['GET'])
def userHome(username):
    # if user is logged in, render user home page
    if 'loggedin' in session and username == session['username']:
        username, userID = session['username'], session['id']
        favoriteDishes=[(dishID, getDishName(dishID)) for dishID in getUserFavs(userID)]
        
        # each item is formatted (dishName, mealAvailability list)
        itemsDates = list()
        for (dishID, dishName) in favoriteDishes:
            itemsDates.append((dishName, getDishAvailability(dishID)))
        
        # gets restaurants following favorited criteria
        cuisineTagExcludeList, cuisineTagIncludeList = list(), list()
        userInclude, userExclude = getUserPreferences(session['id'])
        for tag in CUISINE_TAGS:
            if tag in userExclude: cuisineTagExcludeList.append(tag)
            elif tag in userInclude: cuisineTagIncludeList.append(tag)

        if not itemsDates: itemsDates = None
        data = {
            'itemsDates':itemsDates,
            'userRole':getUserRole(session['id'])
        }
        return render_template('Home.html', username=username, data=data)

    # else, go to generic home page
    return redirect(url_for('home'))
# ===============

# ===== ACCOUNT PAGES =====
@app.route('/Login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('user')
        password = request.form.get('pass')
        res, msg = authenticateAccount(username, password)

        # if account is not authenticated, throw error on login page
        if res != True:
            flash(msg)
            return redirect(url_for("login"))
        
        # else, login to user home page
        session['loggedin'] = True
        session['id'] = msg[0]
        session['username'] = msg[1]
        return redirect(url_for("home"))

    return render_template('Login.html')

@app.route('/CreateAccount/', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        email = request.form.get('email')
        user = request.form.get('user')
        pass1 = request.form.get('pass1')
        pass2 = request.form.get('pass2')
        res, msg = createAccount(email, user, pass1, pass2)

        # if invalid account details inputed, throw error on create page
        if res != True:
            flash(msg)
            return redirect(url_for("create"))
        
        # else, login to user home page
        session['loggedin'] = True
        session['id'] = msg[0]
        session['username'] = msg[1]
        return redirect(url_for("home"))

    return render_template('CreateAccount.html')
# ===============

# ===== GENERAL USER TABS =====
@app.route('/Search/', methods=['GET', 'POST'])
def search():
    # TODO: add search meal bar to search specifically OR select meals to search
    username=session['username'] if 'loggedin' in session else ""
    menuDays, _ = getDateStrings()
    dateParam = [(i, day[0]) for i, day in enumerate(menuDays)]
    DHIncluded, tagIncludeList, tagExcludeList = list(), list(), list()
    completeSearch = False
    restaurants = None
    
    if request.method == 'POST':
        # extracts restaurants
        DHIncluded = request.form.getlist('dining_hall')
        if not bool(DHIncluded): DHIncluded = ['Livingston', 'Brower', 'Busch', 'Neilson']

        # extracts parameters to include and exclude  
        tagExcludeList = list()
        tagIncludeList = synthesizeWhitelist(request.form.getlist('tag'), request.form.getlist('diet'))
        for tag in CUISINE_TAGS + MEAT_TAGS:
            if request.form.get(tag) == 'exclude': tagExcludeList.append(tag)
            elif request.form.get(tag) == 'include': tagIncludeList.append(tag)  
        completeSearch = searchForDish(DHIncluded, tagIncludeList, tagExcludeList)   
        restaurants = None

        # gets off_campus restaurants if selected
        if request.form.get('off_campus') == 'on':
            tagIncludeList.append('off_campus')
            cuisineTagExcludeList, cuisineTagIncludeList = list(), list()
            for tag in CUISINE_TAGS:
                if request.form.get(tag) == 'exclude': cuisineTagExcludeList.append(tag)
                elif request.form.get(tag) == 'include': cuisineTagIncludeList.append(tag)

            restaurants = getRestaurantsUsingTags(cuisineTagIncludeList, cuisineTagExcludeList)
            if not bool(restaurants): restaurants = None

    data = {"username":username,
            "dates":dateParam,
            "mealTimes":MEAL_TIMES,
            "DHIncluded":DHIncluded,
            "include":tagIncludeList,
            "exclude":tagExcludeList,
            "completeSearch":completeSearch,
            "restaurants":restaurants}   
    return render_template('Search.html', data=data)

@app.route('/Menu/', methods=['GET', 'POST'])
def menu():
    username = session['username'] if 'username' in session else ""

    # gets the dates for which we scraped menus
    # menuDays => (dateStr, date.Datetime)
    menuDays, todayStr = getDateStrings()
    dateParam = [(i, day[0]) for i, day in enumerate(menuDays)]

    dhBusyPrediction = checkDiningHallsBusy()

    if request.method == 'GET':
        # TODO: add implementation to default given current time
        # Defaults to Livingston lunch menu (no real reason, just wanted to choose randomly)
        diningHall = "Livingston DH"
        currentDayStr = todayStr[0]
        mealTime = "lunch"
        currentDayDatetime = todayStr[1] 
        checked = False 
        menu = getMenuItems(diningHall, currentDayDatetime, mealTime)
    else:
        mealTime = request.form['meal']
        diningHall = DB_DH_STR[request.form['dining_hall']]
        for day in dateParam:
            if day[0] == int(request.form['date']):
                currentDayStr = day[1]
                break
        for day in menuDays:
            if day[0] == currentDayStr:
                currentDayDatetime = day[1]
                break
        
        if 'apply_filters' in request.form:
            checked = True
            menu= getMenuItemsWithPreferences(userID=session['id'], restaurantName=diningHall, requestedDate=currentDayDatetime, mealTime=mealTime)
        else:
            checked = False
            menu = getMenuItems(diningHall, currentDayDatetime, mealTime)
        
        # sets menu = None if menu is empty
        if not bool(menu): menu = None
    
    data = {"username":username,
            "diningHall":diningHall, 
            "currentDay":currentDayStr,
            "dates":dateParam,
            "mealTime":mealTime,
            "checked":checked,
            "menu":menu,
            "diningHallBusy": dhBusyPrediction}    
    return render_template('Menu.html', data=data)

@app.route('/Restaurants/', methods=['GET', 'POST'])
def restaurants():
    # print("doing something")
    username=session['username'] if 'loggedin' in session else ""
    tag_include_list, tag_exclude_list = list(), list()
    restaurantDict = {}

    if request.method == 'GET':
        restaurantDict = getOffCampusRestaurants()

    elif request.method == 'POST':
        # extracts parameters to include and exclude  
        tag_exclude_list = list()
        tag_include_list = synthesizeWhitelist(request.form.getlist('tag'), request.form.getlist('diet'))
        print(tag_include_list)
        print()

        # for i in ITEMS_TO_CHECK:
        #     if request.form.get(i) == 'exclude': tag_exclude_list.append(i)
        #     elif request.form.get(i) == 'include': tag_include_list.append(i)  

        print(tag_include_list)
        print(tag_exclude_list)

        restaurantDict = getRestaurantsUsingTags(tag_include_list, tag_exclude_list)  

    # print(restaurantDict)

    data = {"username":username,
            "include":tag_include_list,
            "exclude":tag_exclude_list,
            "restaurants":restaurantDict}   

    return render_template('Restaurants.html', data=data)
# ===============

# ===== USER SPECIFIC PAGES =====
@app.route('/UserSettings/', methods=['GET', 'POST'])
def userSettings():
    currentUserID = session['id']
    userWhitelist, userBlacklist = getUserPreferences(currentUserID)
    favDishList = getUserFavs(currentUserID)
   
    if request.method == 'POST':
        tagExcludeList = list()
        tagIncludeList = synthesizeWhitelist(request.form.getlist('tag'), request.form.getlist('diet'))
        favDishList = [int(fav) for fav in request.form.getlist('favs')]
        for tag in CUISINE_TAGS:
            if request.form.get(tag) == 'exclude': tagExcludeList.append(tag)
            elif request.form.get(tag) == 'include': tagIncludeList.append(tag)
        
        # updates user preferences
        clearUserPreferences(currentUserID)
        addUserPreferences(currentUserID, tagIncludeList, tagExcludeList)
        userWhitelist, userBlacklist = getUserPreferences(currentUserID)

        # updates user favorites dishes
        clearUserFavs(currentUserID)
        addUserFavs(currentUserID, favDishList)
    
    data = {
        'username':session['username'],
        'include':userWhitelist,
        'exclude':userBlacklist,
        'favorites':favDishList,
        'dishes':getAllDishes()
    }
    
    return render_template('UserSettings.html', data=data)

# ===== ADMIN CHOICES =====
@app.route('/AddRestaurant/', methods=['GET', 'POST'])
def addRestaurant():
    # if non-admin account tries to access page, redirect to home
    if 'loggedin' not in session: return redirect(url_for("home"))
    userRole = getUserRole(session['id'])
    if userRole != 1: return redirect(url_for("home"))

    # =====
    if request.method == 'POST':
        name = request.form.get('name')
        onCampus = int(request.form.get('oncampus'))
        address = request.form.get('address')
        newTags = request.form.getlist('cuisine')

        # if any field is empty, throw error
        if not bool(name) or not bool(address):
            flash("Please fill out fields!")        
        # if restaurant name already in the database
        elif checkRestaurantExists(name):
            flash("Restaurant already in system!")
        # otherwise, insert the restaurant into database
        else:
            insertRestaurant(name, onCampus, address)
            restaurantID = getRestaurantID(name)
            clearRestaurantTags(restaurantID)
            addRestaurantTags(restaurantID, newTags)  
            return redirect(url_for('chooseRestaurant'))

    return render_template('AddRestaurant.html')

@app.route('/ChooseRestaurant/', methods=['GET', 'POST'])
def chooseRestaurant():
    # if non-admin account tries to access page, redirect to home
    if 'loggedin' not in session: return redirect(url_for("home"))
    userRole = getUserRole(session['id'])
    if userRole != 1: return redirect(url_for("home"))

    # =====

    if request.method == 'POST':
        if request.form.get('submit_button') == 'add':
            return redirect(url_for("addRestaurant"))

        restaurantID = request.form.get('restaurant')
        return redirect(url_for("editRestaurant", restaurantID=restaurantID))

    data={
        'restaurants':getOffCampusRestaurants()
    }
    return render_template('ChooseRestaurant.html', data=data)

@app.route('/EditRestaurant/<restaurantID>/', methods=['GET', 'POST'])
def editRestaurant(restaurantID):
    # if non-admin account tries to access page, redirect to home
    if 'loggedin' not in session: return redirect(url_for("home"))
    userRole = getUserRole(session['id'])
    if userRole != 1: return redirect(url_for("home"))

    # =====

    # if restaurantID is invalid, go to choose restaurant page
    if not checkValidRestaurant(restaurantID): return redirect(url_for('chooseRestaurant'))

    # updates restaurant information in the database
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        newTags = request.form.getlist('cuisine')

        if request.form.get('submit_button') == 'save':
            updateRestaurantInfo(restaurantID, name, address)
            clearRestaurantTags(restaurantID)
            addRestaurantTags(restaurantID, newTags)  
        elif request.form.get('submit_button') == 'delete':
            deleteRestaurant(restaurantID)
            return redirect(url_for("chooseRestaurant"))

    data={
        'username':session['username'],
        'restaurantInfo':(getRestaurantName(restaurantID), getRestaurantAddress(restaurantID)),
        'userRole':getUserRole(session['id']),
        'tags':getRestaurantTags(restaurantID)
    }
    return render_template('EditRestaurant.html', data=data)


@app.route('/ChooseUser/', methods=['GET', 'POST'])
def chooseUser():
    if request.method == 'POST': 
        user_id = request.form.get('user')
        return redirect(url_for("editUser", user_id=user_id))
    
    data={
        'username':session['username'],
        'users':getAllUsers()
    }
    return render_template('ChooseUser.html', data=data)

@app.route('/EditUser/<userID>/', methods=['GET', 'POST'])
def editUser(userID):
    # if dish_id is invalid, go to choose dish page
    if not validUser(userID): return redirect(url_for('chooseUser'))

    # adds new tags to the database
    if request.method == 'POST':
        print(request.form['submit_button'])
        newTags = request.form.getlist('tag')
        #clearDishTags(dish_id)
        #addDishTags(dish_id, newTags)    

    data={
        'username':session['username'],
        'tags':getAllTags(),
        'editUser':getUsername(userID)
    }
    return render_template('EditUser.html', data=data)

# ===============

# ===== RESTAURANT ADMIN TABS =====
@app.route('/ChooseDish/', methods=['GET', 'POST'])
def chooseDish():
    if request.method == 'POST': 
        dishID = request.form.get('dish')
        return redirect(url_for("editTags", dishID=dishID))
    
    data={
        'username':session['username'],
        'dishes':getAllDishes()
    }
    return render_template('ChooseDish.html', data=data)

@app.route('/EditTags/<dishID>/', methods=['GET', 'POST'])
def editTags(dishID):
    # if dishID is invalid, go to choose dish page
    if not checkValidDish(dishID): return redirect(url_for('chooseDish'))

    # adds new tags to the database
    if request.method == 'POST':
        newTags = request.form.getlist('tag')
        clearDishTags(dishID)
        addDishTags(dishID, newTags)    

    data={
        'username':session['username'],
        'tags':getAllTags(),
        'dishName':getDishName(dishID),
        'dishTags':getDishTags(dishID)
    }
    return render_template('EditTags.html', data=data)
# ===============

@app.route('/Home/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='172.16.122.27', port='3030')
