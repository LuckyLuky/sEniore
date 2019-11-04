import os
from flask import Flask, g, request, url_for, render_template, redirect, session, flash
from jinja2 import exceptions
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, SelectField, IntegerField, widgets, validators, PasswordField, SubmitField
from wtforms import RadioField
from flask_wtf.file import FileRequired
from wtforms.validators import InputRequired
from dbaccess import DBAccess
import psycopg2
import configparser 
import hashlib
import sendgrid
from lookup import DictionaryDemandOffer, Services

app = Flask('seniore')

app.config["SECRET_KEY"] = "super tajny klic"

class LoginForm(FlaskForm):
    user = StringField("Uživatel", validators = [InputRequired()], render_kw = dict(class_ = "form-control")) #Přihlašovací jméno
    password = PasswordField("Heslo", validators = [InputRequired()], render_kw = dict(class_ = "form-control")) #Heslo
    submit = SubmitField("Odeslat", render_kw = dict(class_ = "btn btn-outline-primary btn-block"))

class RegistrationFormBase(FlaskForm):
    # firstName     = StringField('First Name',[(validators.length(min=2, max=50))], widget = widgets.Input(input_type = "string"))
    # surname     = StringField('Surname' )
    # email     = StringField('email')
    # address   = StringField('adress')
    # telephone     = StringField('telephone')
    # password     = StringField('password')
    # password2   = StringField('password2')
    demandOffer = RadioField('Nabídka/Poptávka', choices=[('2','nabídka'),('1','poptávka')], default = '2')
    # accept_rules = BooleanField('I accept the site rules')
    checkBoxes = [] # adding dynamically, created in relevant fcn
    checkBoxIndexes = [] 
    # def __init__(self):
    #   self.checkBoxes = []
    #   self.checkBoxIndexes = []

class OverviewFormBase(FlaskForm):
  demandOffer = RadioField('Nabídka/Poptávka', choices=[('2','nabídka'),('1','poptávka')], default = '2')

def regFormBuilder(services):
    class RegistrationForm(RegistrationFormBase):
        pass

    checkBoxIndexes = []
    for (service) in enumerate(services): # get list of services in relevant fcn, all services in db
      setattr(RegistrationForm, 'checkbox%d' % service[1][0],BooleanField(label=service[1][1],id=service[1][0])) # adding to reg. form checkbox for each service (instead of %d put id_service). In services, I get list with fcn row_id, id_services, services_text, thus for id_services I need services [1][0], and for service name I need services [1][1]
      checkBoxIndexes.append(service[1][0])
    
    setattr(RegistrationForm, 'checkBoxIndexes',checkBoxIndexes)
    
    return RegistrationForm()



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
        flash('Uživatel session["user"]{0} {1} přihlášen'.format(userRow[2], userRow[3]))
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
    form = OverviewFormBase()
    services = DBAccess.ExecuteSQL('select * from services')
    addresses = DBAccess.ExecuteSQL('select distinct address from users')
    if request.method == 'GET':
      return render_template('prehled.html', form = form, services = services, addresses = addresses)

    elif request.method == 'POST':
        vysledekselectu = DBAccess.ExecuteSQL('''
        SELECT u.first_name, u.surname, s.category, d.demand_offer, u.address, us.id
        FROM users u
        LEFT JOIN users_services us on us.id_users = u.id 
        LEFT JOIN services s on s.id = us.id_services
        LEFT JOIN demand_offer d on d.id = us.id_demand_offer
        WHERE d.id = %s and s.id = %s and lower(u.address) = lower(%s)
        ORDER BY us.id desc
        LIMIT 10
        ''', (form.demandOffer.data, request.form['category'], request.form['address']))
        if vysledekselectu == None:
          vysledekselectu = []
        return render_template ('prehled_success.html', entries = vysledekselectu)

@app.route('/sluzby', methods=['POST', 'GET'])
def sluzby_upload():
  services = DBAccess.ExecuteSQL('select * from services')
  form = regFormBuilder(services) # put all services to form, but I need to display it - by for cycle below
  form.checkBoxes.clear() # not to have duplicates on website

  for index in form.checkBoxIndexes:
    form.checkBoxes.append(getattr(form,'checkbox%d' % index))  # displaying checkboxes on website

  if form.validate_on_submit(): # if validated, save in db
    nextId = session["id_user"]
    services_checked = []
    for index in form.checkBoxIndexes:
      checkbox = getattr(form,'checkbox%d' % index)
      if(checkbox.data): # for every checked services in form, save..
        existing_combination = DBAccess.ExecuteScalar('select count(*) from users_services where id_users=%s and id_services=%s and id_demand_offer=%s', (nextId,checkbox.id, form.demandOffer.data))
        text = DictionaryDemandOffer.get(form.demandOffer.data,'unknown').lower()
        if existing_combination > 0:
          flash( f'Zadaná kombinace {session["user"]}, {text} a {checkbox.label.text} již existuje.')
        else:
          DBAccess.ExecuteInsert('insert into users_services (id_users, id_services, id_demand_offer) values (%s, %s, %s)', ( nextId,checkbox.id, form.demandOffer.data ))
        services_checked.append(checkbox.label)
    kwargs = {
      'demand_offer': DictionaryDemandOffer.get(form.demandOffer.data, 'unknown'),
      'category': services_checked,
      }
    return render_template('sluzby_success.html', **kwargs)
    
  return render_template('sluzby.html', form = form)

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

@app.route('/email_sent/', methods=['POST'])
def email_sent():
  user = session["user"]
  session["id_user"]
  id_users_services = request.form.get('id', type=int)
  date = request.form.get('date', type=str)
  time = request.form.get('time', type=str)
  info = request.form.get('info', type=str)
  email_user_long = DBAccess.ExecuteSQL('''
        SELECT u.email
        FROM users u
        LEFT JOIN users_services us on us.id_users = u.id 
        LEFT JOIN services s on s.id = us.id_services
        LEFT JOIN demand_offer d on d.id = us.id_demand_offer
        WHERE us.id = %s
        ''', (id_users_services, ))
  email_user = email_user_long[0][0]
  message = {
      'personalizations': [
          {
              'to': [
                  {
                      'email': f'{email_user}'
                  }
              ],
              'subject': 'Seniore'
          }
      ],
      'from': {
          'email': 'noreply@seniore.org'
      },
      'content': [
          {
              'type': 'text/plain',
              'value': f'Uživatel {user} se s Vámi chce setkat dne {date} v {time}. Doplňující informace: {info}. Prosím, potvrďte svůj zájem odpovědí na zobrazený e-mail.'
          }
      ]
  }
  
  sg = sendgrid.SendGridAPIClient(getEmailAPIKey())
  response = sg.send(message)
  print(response.status_code)
  print(response.body)
  print(response.headers)
  return render_template ('email_sent.html')

def getEmailAPIKey():
  API_Key = os.environ.get('SENDGRID_API_KEY')
  if not API_Key:
    configParser = configparser.RawConfigParser()   
    configFilePath = r'config.txt'
    configParser.read(configFilePath)
    API_Key = configParser.get('my-config', 'sendgrid_api_key')
  if not API_Key:
    raise Exception('Could not find API_Key value.')
  return API_Key

@app.route('/match/', methods = ["GET"])
def match():
  id_users_services = request.args.get('id', type=int)
  user_service_requested = DBAccess.ExecuteSQL('''
      SELECT d.demand_offer, s.category
      FROM users u
      LEFT JOIN users_services us on us.id_users = u.id 
      LEFT JOIN services s on s.id = us.id_services
      LEFT JOIN demand_offer d on d.id = us.id_demand_offer
      WHERE us.id = %s
      ''', (id_users_services, ))[0]
  kwargs = {
  'demand_offer': user_service_requested[0],
  'services': user_service_requested[1],
  'id': id_users_services,
  }
  return render_template('/match.html', **kwargs)

if __name__ == '__main__':
    app.debug = True
    host = os.environ.get('IP', '127.0.0.1')
    port = int(os.environ.get('PORT', 8080))
    app.run(host=host, port=port)
