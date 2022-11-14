import os
from server.AccountServices import *
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
    if 'username' not in session:
        return render_template('Search.html', username='')
    return render_template('Search.html', username=session['username'])

@app.route('/UserSettings/', methods=['GET', 'POST'])
def userSettings():
    current_user = session['username'] if 'username' in session else None
    if current_user == None: 
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