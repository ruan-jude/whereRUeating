import os
import datetime
from server.AccountServices import *
from server.DishServices import *
from flask import Flask, render_template, request, redirect, url_for, flash, session

template_dir = os.getcwd() + '/client/'
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'SECRET_KEY'

@app.route('/', methods=['GET'])
@app.route('/Home/', methods=['GET'])
@app.route('/Home/<username>/', methods=['GET'])
def home():
    if 'username' not in session:
        return render_template('Home.html', username='')
    return render_template('Home.html', username=session['username'])

@app.route('/Login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('user')
        password = request.form.get('pass')

        res, msg = authenticate_account(username, password)
        if res != True:
            flash(msg)
            return redirect(url_for("login"))
        
        session['loggedin'] = True
        session['id'] = msg[0]
        session['username'] = msg[1]
        return redirect(url_for("home"))

    return render_template('Login.html')

@app.route('/CreateAccount/', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # collecting form data
        email = request.form.get('email')
        user = request.form.get('user')
        pass1 = request.form.get('pass1')
        pass2 = request.form.get('pass2')

        # inserts data into the database
        res, msg = create_account(email, user, pass1, pass2)
        if res != True:
            flash(msg)
            return redirect(url_for("create"))
        
        session['loggedin'] = True
        session['id'] = msg[0]
        session['username'] = msg[1]
        return redirect(url_for("home"))

    return render_template('CreateAccount.html')

@app.route('/Search/', methods=['GET', 'POST'])
def search():
	return render_template('Search.html')

@app.route('/UserSettings/', methods=['GET', 'POST'])
def userSettings():
    current_user = session['username']
    print(session['username'])

    #pass this into render_template('UserSettings.html', data=user_preferences)x
    user_whitelist, user_blacklist = get_user_preferences(current_user)
    data = user_whitelist + user_blacklist

    #pass this into render_template('UserSettings.html', data=user_preferences)
   
    if request.method == 'GET' and current_user:
        return render_template('UserSettings.html', data=data, username=current_user)
    elif request.method == 'POST':
        tag_exclude_list = request.form.getlist('tag_exclude')
        include_list = synthesize_whitelist(request.form.getlist('tag'), request.form.getlist('diet'))

        print(include_list)

        clear_user_preferences(current_user)
        res = add_user_preferences(current_user, include_list, tag_exclude_list)
        
        user_whitelist, user_blacklist = get_user_preferences(current_user)
        data = user_whitelist + user_blacklist
        return render_template('UserSettings.html', data=data, username=current_user)

@app.route('/Menu/', methods=['GET', 'POST'])
def menu():
    if request.method == 'GET':
        data = {"Livingston" : getMenuItems(datetime.datetime(2022, 11, 13), "Livingston DH", "breakfast"),
                "Busch": getMenuItems(datetime.datetime(2022, 11, 13), "Busch DH", "breakfast"),
                "Brower": getMenuItems(datetime.datetime(2022, 11, 13), "Brower DH", "breakfast"),
                "Nielson": getMenuItems(datetime.datetime(2022, 11, 13), "Nielson DH", "breakfast")
                }
        return render_template('Menu.html', data=data)

    elif request.method == 'POST' and request.form.get('apply_filters') == 'apply_filters_true':
        meal_time = request.form['submit_button']
        current_user = session['username']
        data = {"Livingston" : getMenuItemsWithUserPreferences(current_user, "Livingston DH", datetime.datetime(2022, 11, 13), meal_time),
                "Busch": getMenuItemsWithUserPreferences(current_user, "Busch DH", datetime.datetime(2022, 11, 13), meal_time),
                "Brower": getMenuItemsWithUserPreferences(current_user, "Brower DH", datetime.datetime(2022, 11, 13), meal_time),
                "Nielson": getMenuItemsWithUserPreferences(current_user, "Nielson DH", datetime.datetime(2022, 11, 13), meal_time),
                "checked": True
                }
        return render_template('Menu.html', data=data)

    elif request.method == 'POST':
        meal_time = request.form['submit_button']
        data = {"Livingston" : getMenuItems(datetime.datetime(2022, 11, 13), "Livingston DH", meal_time),
                "Busch": getMenuItems(datetime.datetime(2022, 11, 13), "Busch DH", meal_time),
                "Brower": getMenuItems(datetime.datetime(2022, 11, 13), "Brower DH", meal_time),
                "Nielson": getMenuItems(datetime.datetime(2022, 11, 13), "Nielson DH", meal_time)
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
    app.run(host='172.16.122.27', port='8080')