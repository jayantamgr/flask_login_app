from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "your secret key"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'xxx'
app.config['MYSQL_DB'] = 'loginapp'

mysql = MySQL(app)

@app.route('/')
def main():
	return render_template('main.html')

@app.route('/login/', methods = ['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE username = %s', [username])
		account = cursor.fetchone()
		print(account['password'])
		if account and check_password_hash(account['password'], password):
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
	return redirect(url_for('main'))

@app.route('/login/register/', methods = ['GET', 'POST'])
def register():
	#msg = ''
	new_account_info = None
	if request.method == 'POST':# and 'firstname' in request.form and 'birthdate' in request.form and 'password' in request.form and 'email' in request.form:
		
		firstname = request.form['firstname'] 
		lastname = request.form['lastname']
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		birthdate = request.form['birthdate']
		nationality = request.form['nationality']
		salutation = request.form['salutation']

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
			passw = generate_password_hash(password)
			cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, passw, email))
			mysql.connection.commit()
			last_id = cursor.lastrowid
			cursor.execute('INSERT INTO user VALUES (NULL, %s, %s, %s, %s, %s, %s)', (last_id, salutation, firstname, lastname, birthdate, nationality))
			mysql.connection.commit()
			cursor.execute('SELECT * FROM accounts JOIN user WHERE user.account_id = %s AND accounts.id = %s', [last_id, last_id])
			#msg = 'You have successfully registered'    	
			new_account_info = cursor.fetchone()
			return render_template('welcome.html', new_account_info=new_account_info)	
	elif request.method == 'POST':
		msg = 'Please fill out the form'
	return render_template('register.html')


@app.route('/login/home')
def home():
	if 'loggedin' in session:
		return render_template('home.html', username=session['username'])
	return redirect(url_for('login'))

@app.route('/pythonlogin/profile')
def profile():
    print('x1')
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts JOIN user WHERE user.account_id = %s AND accounts.id = %s', (session['id'], session['id']))
        account = cursor.fetchone()
        # Show the profile page with account info
        cursor.execute('SELECT * FROM education WHERE account_id = %s', [session['id'], ])
        education = cursor.fetchall()    
        print(education)    
        return render_template('profile.html', account=account, education=education)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/pythonlogin/profile/editprofile', methods = ['GET', 'POST', 'PUT'])
def editprofile():
	if 'loggedin' in session:
		if request.method == 'POST':
			print('x1') # and 'course' in request.form and 'institute' in request.form:
			institute = request.form['institute_name']
			course = request.form['course_name']
			degree = request.form['degree']
			country = request.form['country']
			city = request.form['city']
			description = request.form['Description']
			print(description)
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('SELECT * FROM user WHERE account_id = %s', (session['id'], ))
			uid = cursor.fetchone()
			print(uid['id'])
			cursor.execute('INSERT INTO education VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)', (institute, course, degree, city, country, description, uid['id'], session['id'] ))
			mysql.connection.commit()
			return redirect(url_for('profile'))
	return render_template('editprofile.html')




"""
	if 'loggedin' in session:
		firstname = request.form['firstname'] 
		lastname = request.form['lastname']
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		birthdate = request.form['birthdate']
		nationality = request.form['nationality']
		salutation = request.form['salutation']
	"""