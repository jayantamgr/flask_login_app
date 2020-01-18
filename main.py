from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = "your secret key"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '******'
app.config['MYSQL_DB'] = 'loginapp'

mysql = MySQL(app)

@app.route('/login/', methods = ['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['username']
			return redirect(url_for('home'))
		else:
			msg = 'Incorect username/password'

	return render_template('index.html', msg=msg)		

@app.route('/login/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/login/register/', methods = ['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']

		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE username = %s', [username])
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid Email'
		elif not re.match(r'[A-za-z0-9]+', username):
			msg = 'Username must contain only numbers and characters'
		elif not username or not password or not email:
		    msg = 'Please fill out the form'
		else:
		    cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email))
		    mysql.connection.commit()
		    msg = 'You have successfully registered'    	

	elif request.method == 'POST':
		msg = 'Please fill out the form'
	return render_template('register.html', msg=msg)	


@app.route('/login/home')
def home():
	if 'loggedin' in session:
		return render_template('home.html', username=session['username'])
	return redirect(url_for('login'))

@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))