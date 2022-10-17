import os
from flask import Flask, render_template, request
template_dir = os.getcwd() + '/client/'
app = Flask(__name__, template_folder=template_dir)

@app.route('/', methods=['GET'])
def home():
	return render_template('Home.html')

@app.route('/Login.html', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		user = request.form.get('user')
		password = request.form.get('pass')
		return user + ' ' + password
	return render_template('Login.html')

@app.route('/CreateAccount.html', methods=['GET', 'POST'])
def create():
	if request.method == 'POST':
		user = request.form.get('user')
		pass1 = request.form.get('pass1')
		pass2 = request.form.get('pass2')
		return user + ' ' + pass1
	return render_template('CreateAccount.html')

if __name__ == '__main__':
	app.run(host='172.16.122.27', port='3030')
