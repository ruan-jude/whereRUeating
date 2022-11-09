import sys
import atexit

# CHANGE THIS TO MATCH THE DIRECTORY IN YOUR LOCAL COPY/MACHINE OR WHEREVER YOU'RE RUNNING THE SERVER
sys.path.insert(1, "/home/cch106/whereRUeating-main/server/")

import os
from server.AccountServices import *
from flask import Flask, render_template, request, redirect, url_for, flash, session

template_dir = os.getcwd() + '/client/'
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'SECRET_KEY'
#session.clear()

@app.route('/', methods=['GET'])
@app.route('/Home/', methods=['GET'])
def home():
    return render_template('Home.html')

@app.route('/Home/<username>/', methods=['GET'])
def userHome():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('UserHome.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('home'))

@app.route('/Login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('user')
        password = request.form.get('pass')

        res, msg = authenticate_account(username, password)
        if res != True:
            flash(msg)
            return redirect(url_for("home"))
        
        session['loggedin'] = True
        session['id'] = msg[0]
        session['username'] = msg[1]
        return redirect(url_for("userHome"))

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
        res = create_account(email, user, pass1, pass2)
        flash(res)
        return redirect(url_for("home"))

    return render_template('CreateAccount.html')

@app.route('/Search/', methods=['GET', 'POST'])
def search():
	return render_template('Search.html')

@app.route('/UserSettings/', methods=['GET', 'POST'])
def userSettings():
    print(session)
    print('username' in session)
    current_user = session['username'] if 'username' in session else None
    print(current_user)
    if current_user == None: 
        print("here")
        return redirect(url_for('login'))

    #pass this into render_template('UserSettings.html', data=user_preferences)x
    user_whitelist, user_blacklist = get_user_preferences(current_user)
    data = user_whitelist + user_blacklist
    if request.method == 'GET':
        return render_template('UserSettings.html', data=data)
    elif request.method == 'POST':
        tag_exclude_list = request.form.getlist('tag_exclude')
        include_list = synthesize_whitelist(request.form.getlist('tag'), request.form.getlist('diet'))

        res = add_user_preferences(current_user, include_list, tag_exclude_list)
        
        user_whitelist, user_blacklist = get_user_preferences(current_user)
        data = user_whitelist + user_blacklist
        return render_template('UserSettings.html', data=data)


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