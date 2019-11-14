import os
from flask import Flask, Blueprint, g, request, url_for, render_template, redirect, session, flash
from jinja2 import exceptions
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, SelectField, IntegerField, widgets, validators, PasswordField, SubmitField, RadioField, FileField
from flask_wtf.file import FileRequired
from wtforms.validators import InputRequired
from werkzeug.utils import secure_filename
from dbaccess import DBAccess
import psycopg2
import configparser 
import hashlib
import sendgrid
from lookup import DictionaryDemandOffer, Services
from datetime import datetime, date, time
from flask import current_app as app
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

blueprint = Blueprint('profile_bp', __name__, template_folder='templates')

class OverviewFormBase(FlaskForm):
  demandOffer = RadioField('Nabídka/Poptávka', choices=[('2','nabídka'),('1','poptávka')], default = '2')

@blueprint.route('/profil', methods=['GET', 'POST'])
def profil():
  nazev = f'{str(session["id_user"])}.jpg'
  latitude =str( DBAccess.ExecuteScalar('select latitude from users where id = %s', (session["id_user"],)))
  longitude = str(DBAccess.ExecuteScalar('select longitude from users where id = %s', (session["id_user"],)))
  nazevUrl = url_for('static', filename='users_images/' + nazev )
  username = session['user']

  if request.method == 'GET':
      vysledekselectu = DBAccess.ExecuteSQL('select s.category as category, d.demand_offer as demand_offer from users u left join users_services us on us.id_users = u.id left join services s on s.id = us.id_services left join demand_offer d on d.id = us.id_demand_offer where u.id = %s', (session["id_user"],))
  sndmap = Map(
    identifier="sndmap",
    lat=latitude,
    lng=longitude,
    report_clickpos=True,
    clickpos_uri="/clickpost/",
    markers=[
    {
    'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
    'lat': latitude,
    'lng':longitude,
    'infobox': f'<b>{username}</b><img class=img_mapa src= {nazevUrl}/>'
    }
    ]
    )
  
  return render_template ('profil.html', entries = vysledekselectu, nazev = nazev, sndmap = sndmap)

# @blueprint.route('/prehled', methods=['POST', 'GET'])
# def prehled_filtr():
#     form = OverviewFormBase()
#     services = DBAccess.ExecuteSQL('select * from services')
#     addresses = DBAccess.ExecuteSQL('select distinct address from users')
#     if request.method == 'GET':
#       return render_template('prehled.html', form = form, services = services, addresses = addresses)

#     elif request.method == 'POST':
#         vysledekselectu = DBAccess.ExecuteSQL('''
#         SELECT u.first_name, u.surname, s.category, d.demand_offer, u.address, us.id
#         FROM users u
#         LEFT JOIN users_services us on us.id_users = u.id 
#         LEFT JOIN services s on s.id = us.id_services
#         LEFT JOIN demand_offer d on d.id = us.id_demand_offer
#         WHERE d.id = %s and s.id = %s and lower(u.address) = lower(%s)
#         ORDER BY us.id desc
#         LIMIT 10
#         ''', (form.demandOffer.data, request.form['category'], request.form['address']))
#         if vysledekselectu == None:
#           vysledekselectu = []
#         return render_template ('prehled_success.html', entries = vysledekselectu)


