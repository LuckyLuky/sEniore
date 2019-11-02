import os
from flask import Flask, g, request, url_for, render_template, redirect, session, flash
from jinja2 import exceptions
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, SelectField, IntegerField, widgets, validators, PasswordField, SubmitField
from flask_wtf.file import FileRequired
from wtforms.validators import InputRequired
from dbaccess import DBAccess
import psycopg2
import configparser 
import hashlib

app = Flask('seniore')

app.config["SECRET_KEY"] = "super tajny klic"

class LoginForm(FlaskForm):
    user = StringField("Uživatel", validators = [InputRequired()], render_kw = dict(class_ = "form-control")) #Přihlašovací jméno
    password = PasswordField("Heslo", validators = [InputRequired()], render_kw = dict(class_ = "form-control")) #Heslo
    submit = SubmitField("Odeslat", render_kw = dict(class_ = "btn btn-outline-primary btn-block"))

@app.route('/login/', methods = ["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.user.data
        userRow = DBAccess.ExecuteSQL('select email, password, first_name, surname, id from users where email like %s',(user,))
        
        if(userRow == None):
          flash('Uživatel nenalezen')
          return render_template("login.html", form = form)
        
        userRow = userRow[0] # execute sql gets list with one item, ie:[(email, password, first_name, surname, id)], we need just (), ie tuple
        md5Pass = hashlib.md5(str(form.password.data).encode()).hexdigest()
        if(userRow[1]!=md5Pass): # check if second item is equal to hashed password
          flash('Špatné heslo')
          return render_template("login.html", form = form)
              
        session["user"] = user
        session["id_user"] = userRow[4]
        flash('Uživatel {0} {1} přihlášen'.format(userRow[2], userRow[3]))
        return redirect(url_for('profil'))
    return render_template("login.html", form = form)

@app.route('/logout/', methods = ["GET", "POST"])
def odhlasit():
    session.pop("user", None)
    session.pop("id_user", None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template ('layout.html')

@app.route('/profil', methods=['GET', 'POST'])
def profil():
    if request.method == 'GET':
        vysledekselectu = DBAccess.ExecuteSQL('select s.category as category, d.demand_offer as demand_offer from users u left join users_services us on us.id_users = u.id left join services s on s.id = us.id_services left join demand_offer d on d.id = us.id_demand_offer where u.id = %s', (session["id_user"],))
    return render_template ('profil.html', entries = vysledekselectu)

@app.route('/prehled', methods=['POST', 'GET'])
def prehled_filtr():
    if request.method == 'GET':
      return render_template('prehled.html')
    elif request.method == 'POST':
        vysledekselectu = DBAccess.ExecuteSQL('select u.first_name as first_name, u.surname as surname, s.category as category, d.demand_offer as demand_offer, u.address as address from users u left join users_services us on us.id_users = u.id left join services s on s.id = us.id_services left join demand_offer d on d.id = us.id_demand_offer where d.id = %s and s.id = %s and lower(u.address) = lower(%s) limit 10', (request.form['demand_offer'], request.form['category'], request.form['address']))
        return render_template ('prehled_success.html', entries = vysledekselectu)

@app.route('/sluzby', methods=['POST', 'GET'])
def sluzby_upload(): 
  # kdyz vyberu demand, ulozi se do db dvakrat??
    if request.method == 'GET':
        return render_template('sluzby.html')
    elif request.method == 'POST':

      if request.form['demand_offer']==2:
        textDemandOffer = 'nabidka'
      else:
        textDemandOffer = 'poptavka'
        kwargs = {
            'demand_offer': textDemandOffer,
            'category': request.form['category'],
            'secret_key': request.form['SECRET_KEY'],
            'submit_value': request.form['submit'],
        }
        DBAccess.ExecuteInsert('insert into users_services (id_demand_offer, id_services, id_users) values (%s, %s, %s)', (request.form['demand_offer'], request.form['category'], session["id_user"]))
        return render_template('sluzby_success.html', **kwargs)

@app.route('/registrace')
def registrace():
    return render_template ('registrace.html')

@app.route('/add_name', methods=['POST'])
def add_name():
    kwargs = {
      'first_name': request.form['first_name'],
      'surname': request.form['surname'],
      'email': request.form['email'],
      'address': request.form['address'],
      'telephone': request.form['telephone'],
      'password': request.form['password']
    }
    unique_number_users_long = DBAccess.ExecuteSQL('SELECT nextval(\'users_id_seq\')')
    unique_number_users = unique_number_users_long[0]
    DBAccess.ExecuteInsert ('insert into users (id, first_name, surname, email, address, telephone, password) values (%s, %s, %s, %s, %s, %s, md5(%s))',
    (unique_number_users, request.form['first_name'], request.form['surname'], request.form['email'], request.form['address'], request.form['telephone'], request.form['password']))
    return render_template ('/registrace_success.html', **kwargs)


if __name__ == '__main__':
    app.debug = True
    host = os.environ.get('IP', '127.0.0.1')
    port = int(os.environ.get('PORT', 8080))
    app.run(host=host, port=port)
