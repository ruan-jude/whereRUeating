import os
from server.AccountServices import *
from flask import Flask, render_template, request, redirect, url_for, flash

template_dir = os.getcwd() + '/client/'
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'SECRET_KEY'

@app.route('/', methods=['GET'])
def home():
    return render_template('Home.html')

@app.route('/Login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('user')
        password = request.form.get('pass')

        res = verify_password(username, password)
        flash(res)
        return redirect(url_for("home"))
    return render_template('Login.html')

@app.route('/CreateAccount.html', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # collecting form data
        user = request.form.get('user')
        pass1 = request.form.get('pass1')
        pass2 = request.form.get('pass2')

        # inserts data into the database
        res = create_account(user+'@gmail.com', user, pass1, pass2)
        flash(res)
        return redirect(url_for("home"))
    return render_template('CreateAccount.html')

@app.route('/Search.html', methods=['GET', 'POST'])
def search():
	return render_template('Search.html')

@app.route('/UserSettings.html', methods=['GET', 'POST'])
def userSettings():
	return render_template('UserSettings.html')

if __name__ == '__main__':
    app.run(host='172.16.122.27', port='8080')
