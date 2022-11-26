import os, calendar
from datetime import datetime, timedelta
from server.AccountServices import *
from server.DishServices import *
from flask import Flask, render_template, request, redirect, url_for, flash, session

template_dir = os.getcwd() + '/client/'
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'SECRET_KEY'

''' 
FUNCTIONING
'''
@app.route('/', methods=['GET'])
def home():
    # if user is logged in, go to user home page
    if 'loggedin' in session:
        return redirect(url_for("userHome", username=session['username']))
    
    # else, go to generic home page
    return render_template('Home.html', username="", data="")

'''
FUNCTIONING
'''
@app.route('/Home/<username>/', methods=['GET'])
def userHome(username):
    # if user is logged in, render user home page
    if 'loggedin' in session and username == session['username']:
        username, userID = session['username'], session['id']
        favoriteDishes=[(dishID, getDishName(dishID)) for dishID in getUserFavs(userID)]
        
        # each item is formatted (dishName, mealAvailability list)
        itemsDates = list()
        for (dishID, dishName) in favoriteDishes:
            itemsDates.append((dishName, getMealAvailability(dishID)))
        
        # if no favoriteDishes, set to None
        if not itemsDates: itemsDates = None
        
        data = {
            'itemsDates':itemsDates
        }
        return render_template('Home.html', username=username, data=data)

    # else, go to generic home page
    return redirect(url_for('home'))

'''
FUNCTIONING
'''
@app.route('/Login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('user')
        password = request.form.get('pass')
        res, msg = authenticate_account(username, password)

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

'''
FUNCTIONING
'''
@app.route('/CreateAccount/', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        email = request.form.get('email')
        user = request.form.get('user')
        pass1 = request.form.get('pass1')
        pass2 = request.form.get('pass2')
        res, msg = create_account(email, user, pass1, pass2)

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

'''
Can only access this if logged in
FUNCTIONING
'''
@app.route('/UserSettings/', methods=['GET', 'POST'])
def userSettings():
    current_user_id = session['id']
    user_whitelist, user_blacklist = get_user_preferences(current_user_id)
    fav_dish_list = getUserFavs(current_user_id)
   
    if request.method == 'POST':
        tag_exclude_list = list()
        tag_include_list = synthesize_whitelist(request.form.getlist('tag'), request.form.getlist('diet'))
        fav_dish_list = [int(fav) for fav in request.form.getlist('favs')]
        for i in ITEMS_TO_CHECK:
            if request.form.get(i) == 'exclude': tag_exclude_list.append(i)
            elif request.form.get(i) == 'include': tag_include_list.append(i)
        
        # updates user preferences
        clear_user_preferences(current_user_id)
        add_user_preferences(current_user_id, tag_include_list, tag_exclude_list)
        user_whitelist, user_blacklist = get_user_preferences(current_user_id)

        # updates user favorites dishes
        clearUserFavs(current_user_id)
        addUserFavs(current_user_id, fav_dish_list)
    
    data = {
        'username':session['username'],
        'include':user_whitelist,
        'exclude':user_blacklist,
        'favorites':fav_dish_list,
        'dishes':getAllMenuItems()
    }
    print(data['favorites'])
    return render_template('UserSettings.html', data=data)

'''
Can only access this if logged in
FUNCTIONING
'''
@app.route('/ChooseDish/', methods=['GET', 'POST'])
def chooseDish():
    if request.method == 'POST': 
        dish_id = request.form.get('dish')
        return redirect(url_for("editTags", dish_id=dish_id))
    
    data={
        'username':session['username'],
        'dishes':getAllMenuItems()
    }
    return render_template('ChooseDish.html', data=data)

'''
Can only access this if logged in
FUNCTIONING
'''
@app.route('/EditTags/<dish_id>/', methods=['GET', 'POST'])
def editTags(dish_id):
    # if dish_id is invalid, go to choose dish page
    if not validDish(dish_id): return redirect(url_for('chooseDish'))

    # adds new tags to the database
    if request.method == 'POST':
        newTags = request.form.getlist('tag')
        clearDishTags(dish_id)
        addDishTags(dish_id, newTags)    

    data={
        'username':session['username'],
        'tags':getAllTags(),
        'dishName':getDishName(dish_id),
        'dishTags':getDishTags(dish_id)
    }
    return render_template('EditTags.html', data=data)

'''
FUNCTIONING
'''
@app.route('/Search/', methods=['GET', 'POST'])
def search():
    # TODO: add search meal bar to search specifically OR select meals to search
    username=session['username'] if 'loggedin' in session else ""
    menuDays, _ = getDateStr()
    dateParam = [(i, day[0]) for i, day in enumerate(menuDays)]
    restaurants_included, tag_include_list, tag_exclude_list = list(), list(), list()
    completeSearch = False
    
    if request.method == 'POST':
        # extracts restaurants
        restaurants_included = request.form.getlist('restaurant')
        if not bool(restaurants_included): restaurants_included = ['Livingston', 'Brower', 'Busch', 'Nielson']

        # extracts parameters to include and exclude  
        tag_exclude_list = list()
        tag_include_list = synthesize_whitelist(request.form.getlist('tag'), request.form.getlist('diet'))
        for i in ITEMS_TO_CHECK:
            if request.form.get(i) == 'exclude': tag_exclude_list.append(i)
            elif request.form.get(i) == 'include': tag_include_list.append(i)  
        completeSearch = searchMenuItems(restaurants_included, tag_include_list, tag_exclude_list)       

    data = {"username":username,
            "dates":dateParam,
            "meal_times":MEAL_TIMES,
            "restaurants_included":restaurants_included,
            "include":tag_include_list,
            "exclude":tag_exclude_list,
            "complete_search":completeSearch}   
    return render_template('Search.html', data=data)

'''
FUNCTIONING
'''
@app.route('/Menu/', methods=['GET', 'POST'])
def menu():
    username = session['username'] if 'username' in session else ""

    # gets the dates for which we scraped menus
    # menuDays = (dateStr, date.Datetime)
    menuDays, todayStr = getDateStr()
    dateParam = [(i, day[0]) for i, day in enumerate(menuDays)]

    if request.method == 'GET':
        # TODO: add implementation to default given current time
        # Defaults to Livingston lunch menu (no real reason, just wanted to choose randomly)
        dining_hall = "Livingston DH"
        current_day_str = todayStr[0]
        meal_time = "lunch"
        current_day_datetime = todayStr[1] 
        checked = False 
        menu = getMenuItems(dining_hall, current_day_datetime, meal_time)
    else:
        meal_time = request.form['meal']
        dining_hall = DB_DH_STR[request.form['dining_hall']]
        for day in dateParam:
            if day[0] == int(request.form['date']):
                current_day_str = day[1]
                break
        for day in menuDays:
            if day[0] == current_day_str:
                current_day_datetime = day[1]
                break
        
        if 'apply_filters' in request.form:
            checked = True
            menu= getMenuItemsWithUserPreferences(session['id'], dining_hall, current_day_datetime, meal_time)
        else:
            checked = False
            menu = getMenuItems(dining_hall, current_day_datetime, meal_time)
    
    data = {"username":username,
            "dining_hall":dining_hall, 
            "current_day":current_day_str,
            "dates":dateParam,
            "meal_time":meal_time,
            "menu_empty":bool(menu),
            "checked":checked,
            "menu":menu}    
    return render_template('Menu.html', data=data)

'''
FUNCTIONING
'''
@app.route('/Home/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='172.16.122.27', port='8080')
