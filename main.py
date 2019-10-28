import os
from flask import Flask, g, request, url_for, render_template, redirect, session
from jinja2 import exceptions
import psycopg2
import configparser 
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, SelectField, IntegerField, widgets, validators, PasswordField, SubmitField
from flask_wtf.file import FileRequired
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired

app = Flask('seniore')

app.config["SECRET_KEY"] = "super tajny klic"

configParser = configparser.RawConfigParser()   
configFilePath = r'config.txt'
configParser.read(configFilePath)

class LoginForm(FlaskForm):
    user = StringField("Uživatel", validators = [InputRequired()], render_kw = dict(class_ = "form-control")) #Přihlašovací jméno
    password = PasswordField("Heslo", validators = [InputRequired()], render_kw = dict(class_ = "form-control")) #Heslo
    submit = SubmitField("Odeslat", render_kw = dict(class_ = "btn btn-outline-primary btn-block"))

@app.route('/login/', methods = ["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.user.data
        password = form.password.data
        if password == "letmein":
            session["user"] = user
    return render_template('login.html', form = form)



@app.route('/logout/', methods = ["GET", "POST"])
def odhlasit():
    session.pop("user", None)
    return redirect(url_for('login'))

def get_db():
  con = psycopg2.connect(user = configParser.get('my-config', 'user'),
                      password = configParser.get('my-config', 'password'),
                      host = configParser.get('my-config', 'host'),
                      port = configParser.get('my-config', 'port'),
                      database = configParser.get('my-config', 'database'))
  return con


@app.route('/')
def index():
    return render_template ('layout.html')

@app.route('/registrace')
def registrace():
    return render_template ('registrace.html')

@app.route('/prehled', methods=['POST', 'GET'])
def prehled_filtr():
    if request.method == 'GET':
      return render_template('prehled.html')
    elif request.method == 'POST':
        user = {
            'demand_offer': request.form['demand_offer'],
            'category': request.form['category'],
            'address': request.form['address'],
            'secret_key': request.form['SECRET_KEY'],
            'submit_value': request.form['submit'],
          }
        db_connection = get_db()
        cursor = db_connection.cursor()
        cursor.execute('select u.first_name as first_name, u.surname as surname, s.category as category, d.demand_offer as demand_offer, u.address as address from users u left join users_services us on us.id_users = u.id left join services s on s.id = us.id_services left join demand_offer d on d.id = us.id_demand_offer where d.id = %s and s.id = %s and lower(u.address) = lower(%s) limit 10', (request.form['demand_offer'], request.form['category'], request.form['address']))
        entries = cursor.fetchall()
        return render_template ('prehled_success.html', entries = entries)

@app.route('/sluzby', methods=['POST', 'GET'])
def sluzby_upload():
    if request.method == 'GET':
        return render_template('sluzby.html')
    elif request.method == 'POST':
        kwargs = {
            'first_name': request.form['first_name'],
            'surname': request.form['surname'],
            'email': request.form['email'],
            'address': request.form['address'],
            'telephone': request.form['telephone'],
            'demand_offer': request.form['demand_offer'],
            'category': request.form['category'],
            'secret_key': request.form['SECRET_KEY'],
            'submit_value': request.form['submit'],
        }
        db_connection = get_db()
        cursor = db_connection.cursor()
        cursor.execute('SELECT nextval(\'users_id_seq\')')
        unique_number_users = cursor.fetchone()
        cursor.execute('insert into users (id, first_name, surname, email, address, telephone) values (%s, %s, %s, %s, %s, %s)',
         (unique_number_users, request.form['first_name'], request.form['surname'], request.form['email'], request.form['address'], request.form['telephone']))
        cursor.execute('SELECT nextval(\'users_services_id_seq\')')
        cursor.execute('insert into users_services (id_demand_offer, id_services, id_users) values (%s, %s, %s)',
        (request.form['demand_offer'], request.form['category'], unique_number_users))
        db_connection.commit()
        return render_template('sluzby_success.html', **kwargs)

@app.route('/succes')
def success():
    return render_template ('success.html')

@app.route('/add_name', methods=['POST'])
def add_name():
    # Získá připojení k databází
    db_connection = get_db()
    cursor = db_connection.cursor()
    unique_number = request.form['id']
    first_name = request.form['first_name']
    surname = request.form['surname']
    email = request.form['email']
    address = request.form['address']
    telephone = request.form['telephone']
    password = request.form['password']
    cursor.execute('insert into users (id, first_name, surname, email, address, telephone, password) values (%s, %s, %s, %s, %s, %s, %s)',
    (unique_number, first_name, surname, email, address, telephone, password))
    db_connection.commit()
    return render_template ('/success.html')


if __name__ == '__main__':
    app.debug = True
    host = os.environ.get('IP', '127.0.0.1')
    port = int(os.environ.get('PORT', 8080))
    app.run(host=host, port=port)
