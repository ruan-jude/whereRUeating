import os, datetime
from server.AccountServices import *
from server.DishServices import *
from flask import Flask, render_template, request, redirect, url_for, flash, session

template_dir = os.getcwd() + '/client/'
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'SECRET_KEY'

@app.route('/', methods=['GET'])
def home():
    # if user is logged in, go to user home page
    if 'loggedin' in session:
        return redirect(url_for("userHome", username=session['username']))
    
    # else, go to generic home page
    return render_template('Home.html', username="")

@app.route('/Home/<username>/', methods=['GET'])
def userHome(username):
    # if user is logged in, render user home page
    if 'loggedin' in session and username == session['username']:
        return render_template('Home.html', username=session['username'])

    # else, go to generic home page
    return redirect(url_for('home'))

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

@app.route('/Search/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        print("Searching...")
        return
    
    # if user is logged in, pass username
    if 'loggedin' in session:
        return render_template('Search.html', username=session['username'])

    # else, pass empty
    return render_template('Search.html', username="")

'''
Can only access this if logged in
'''
@app.route('/UserSettings/', methods=['GET', 'POST'])
def userSettings():
    current_user_id = session['id']
    user_whitelist, user_blacklist = get_user_preferences(current_user_id)
   
    if request.method == 'POST':
        # list of items that you can exclude or include
        items_exclude = ['chicken', 'pork', 'beef', 'seafood', 'dairy', 'nuts', 'chinese', 'indian', 'mexican', 'italian', 'japanese', 'cafe']
        
        tag_exclude_list = list()
        tag_include_list = synthesize_whitelist(request.form.getlist('tag'), request.form.getlist('diet'))
        for i in items_exclude:
            if request.form.get(i) == 'exclude': tag_exclude_list.append(i)
            elif request.form.get(i) == 'include': tag_include_list.append(i)
        
        clear_user_preferences(current_user_id)
        add_user_preferences(current_user_id, tag_include_list, tag_exclude_list)
        user_whitelist, user_blacklist = get_user_preferences(current_user_id)

        flash('Updated preferences for %s!' % (session['username'],))
        return render_template('UserSettings.html', include=user_whitelist, exclude=user_blacklist, username=session['username'])
    
    return render_template('UserSettings.html', include=user_whitelist, exclude=user_blacklist, username=session['username'])

'''
Can only access this if logged in
'''
@app.route('/ChooseDish/', methods=['GET', 'POST'])
def chooseDish():
    dishes = getAllMenuItems()

    if request.method == 'POST': 
        dish_id = request.form.get('dish')
        return redirect(url_for("editTags", dish_id=dish_id))
        
    return render_template('ChooseDish.html', dishes=dishes, username=session['username'])

'''
Can only access this if logged in
'''
@app.route('/EditTags/<dish_id>/', methods=['GET', 'POST'])
def editTags(dish_id):
    # TODO: add implementation for invalid dish_id
    if not validDish(dish_id):
        return redirect(url_for('chooseDish'))

    tags = getAllTags()
    dishName = getDishName(dish_id)

    if request.method == 'POST':
        newTags = request.form.getlist('tag')
        clearDishTags(dish_id)
        addDishTags(dish_id, newTags)
        dishTags = getDishTags(dish_id)
        return render_template('EditTags.html', tags=tags, dishName=dishName, dishTags=dishTags, username=session['username'])
    
    dishTags = getDishTags(dish_id)
    return render_template('EditTags.html', tags=tags, dishName=dishName, dishTags=dishTags, username=session['username'])

@app.route('/Menu/', methods=['GET', 'POST'])
def menu():
    if request.method == 'GET':
        data = {"Livingston" : getMenuItems(datetime.datetime(2022, 11, 3), "Livingston DH", "breakfast"),
                "Busch": getMenuItems(datetime.datetime(2022, 11, 3), "Busch DH", "breakfast"),
                "Brower": getMenuItems(datetime.datetime(2022, 11, 3), "Brower DH", "breakfast"),
                "Nielson": getMenuItems(datetime.datetime(2022, 11, 3), "Nielson DH", "breakfast")
                }
        return render_template('Menu.html', data=data)

    elif request.method == 'POST' and request.form.get('apply_filters') == 'apply_filters_true':
        meal_time = request.form['submit_button']
        current_user = session['username']
        data = {"Livingston" : getMenuItemsWithUserPreferences(current_user, "Livingston DH", datetime.datetime(2022, 11, 3), meal_time),
                "Busch": getMenuItemsWithUserPreferences(current_user, "Busch DH", datetime.datetime(2022, 11, 3), meal_time),
                "Brower": getMenuItemsWithUserPreferences(current_user, "Brower DH", datetime.datetime(2022, 11, 3), meal_time),
                "Nielson": getMenuItemsWithUserPreferences(current_user, "Nielson DH", datetime.datetime(2022, 11, 3), meal_time),
                "checked": True
                }
        return render_template('Menu.html', data=data)

    elif request.method == 'POST':
        meal_time = request.form['submit_button']
        data = {"Livingston" : getMenuItems(datetime.datetime(2022, 11, 3), "Livingston DH", meal_time),
                "Busch": getMenuItems(datetime.datetime(2022, 11, 3), "Busch DH", meal_time),
                "Brower": getMenuItems(datetime.datetime(2022, 11, 3), "Brower DH", meal_time),
                "Nielson": getMenuItems(datetime.datetime(2022, 11, 3), "Nielson DH", meal_time)
                }
        return render_template('Menu.html', data=data)

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
