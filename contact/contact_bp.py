import os
from flask import Flask, Blueprint, g, request, url_for, render_template, redirect, session, flash
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
from datetime import datetime, date, time

blueprint = Blueprint('contact_bp', __name__, template_folder='templates')

@blueprint.route('/match/', methods = ["GET"])
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


@blueprint.route('/email_sent/', methods=['POST'])
def email_sent():
  user = session["user"]
  session["id_user"]
  id_users_services = request.form.get('id', type=int)
  date = request.form.get('date', type=str)
  time = request.form.get('time', type=str)
  strDateTime = f'{date} {time}'
  dt = datetime.strptime(strDateTime, '%Y-%m-%d %H:%M')

  info = request.form.get('info', type=str)
  email_user_long = DBAccess.ExecuteSQL('''
        SELECT u.email, u.id, s.id
        FROM users u
        LEFT JOIN users_services us on us.id_users = u.id 
        LEFT JOIN services s on s.id = us.id_services
        LEFT JOIN demand_offer d on d.id = us.id_demand_offer
        WHERE us.id = %s
        ''', (id_users_services, ))
  email_user = email_user_long[0][0]
  offeringUserId = email_user_long[0][1]
  services_id = email_user_long[0][2]

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

  DBAccess.ExecuteInsert('INSERT INTO requests (id_users_demand, id_users_offer, id_services, timestamp, date_time, add_information, id_requests_status) values (%s,%s,%s,now(),%s,%s,%s)', (session['id_user'],offeringUserId, services_id,dt,info,1 ))
  response = sg.send(message)
  print(response.status_code)
  print(response.body)
  print(response.headers)
  return render_template ('email_sent.html')



