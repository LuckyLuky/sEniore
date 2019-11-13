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

blueprint = Blueprint('serviceReg_bp', __name__, template_folder='templates')

class RegistrationFormBase(FlaskForm):
    demandOffer = RadioField('Nabídka/Poptávka', choices=[('2','nabídka'),('1','poptávka')], default = '2')
    checkBoxes = [] # adding dynamically, created in relevant fcn
    checkBoxIndexes = [] 

def regFormBuilder(services):
    class RegistrationForm(RegistrationFormBase):
        pass

    checkBoxIndexes = []
    for (service) in enumerate(services): # get list of services in relevant fcn, all services in db
      setattr(RegistrationForm, 'checkbox%d' % service[1][0],BooleanField(label=service[1][1],id=service[1][0])) # adding to reg. form checkbox for each service (instead of %d put id_service). In services, I get list with fcn row_id, id_services, services_text, thus for id_services I need services [1][0], and for service name I need services [1][1]
      checkBoxIndexes.append(service[1][0])
    
    setattr(RegistrationForm, 'checkBoxIndexes',checkBoxIndexes)
    
    return RegistrationForm()

@blueprint.route('/sluzby', methods=['POST', 'GET'])
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