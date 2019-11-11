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

blueprint = Blueprint('request_bp', __name__, template_folder='templates')

@blueprint.route('/requests', methods = ["GET", "POST"])
def requests():
  requests = DBAccess.ExecuteSQL(
    '''select
          ud.first_name,
          ud.surname,
          ud.address,
          ud.email,
          ud.telephone,
          uo.first_name,
          uo.surname,
          uo.address,
          uo.email,
          uo.telephone,
          s.category,
          r.date_time,
          r.add_information,
          r.timestamp,
          rs.status,
          r.id
        from requests r
        inner join services s on r.id_services = s.id 
        inner join users ud on r.id_users_demand = ud.id
        inner join users uo on r.id_users_offer = uo.id
        inner join requests_status rs on r.id_requests_status = rs.id''')
  return render_template('requests.html', entries = requests)

@blueprint.route('/requests_detail', methods = ["GET", "POST"])
def requests_detail():
  rid = request.args.get('id', type=int)
  
  if request.method == 'POST':
    status = request.form['submit_button']
    DBAccess.ExecuteUpdate('UPDATE requests SET id_requests_status= %s where id= %s',(status,rid))
  rid = request.args.get('id', type=int)
  requests = DBAccess.ExecuteSQL(
    '''select
          ud.first_name,
          ud.surname,
          ud.address,
          ud.email,
          ud.telephone,
          uo.first_name,
          uo.surname,
          uo.address,
          uo.email,
          uo.telephone,
          s.category,
          r.date_time,
          r.add_information,
          	to_char(r.timestamp, 'YYYY-mm-DD HH12:MI:SS'),
          rs.status,
          r.id
        from requests r
        inner join services s on r.id_services = s.id 
        inner join users ud on r.id_users_demand = ud.id
        inner join users uo on r.id_users_offer = uo.id
        inner join requests_status rs on r.id_requests_status = rs.id
        where r.id =%s''',(rid,))
  return render_template('requests_detail.html', entries = requests[0])