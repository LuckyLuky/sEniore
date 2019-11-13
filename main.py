import os
from flask import Flask, g, request, url_for, render_template, redirect, session, flash
from jinja2 import exceptions
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, SelectField, IntegerField, widgets, validators, PasswordField, SubmitField, FileField
from wtforms import RadioField
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

app = Flask('seniore')

app.config["SECRET_KEY"] = "super tajny klic"

UPLOAD_FOLDER = app.static_folder + "/users_images/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

from login import login_bp
app.register_blueprint(login_bp.blueprint)

from profile_user import profile_bp
app.register_blueprint(profile_bp.blueprint)

from serviceReg import serviceReg_bp
app.register_blueprint(serviceReg_bp.blueprint)

from overview import overview_bp
app.register_blueprint(overview_bp.blueprint)

from contact import contact_bp
app.register_blueprint(contact_bp.blueprint)

from request_user import request_bp
app.register_blueprint(request_bp.blueprint)




class FileFormular(FlaskForm):
    soubor = FileField("Vlož obrázek", validators = [FileRequired()])
    submit = SubmitField("Odeslat", render_kw = dict(class_ = "btn btn-outline-primary btn-block"))

@app.route("/foto/", methods = ["GET", "POST"])
def photo():
    form = FileFormular()
    nazev = f'{str(session["id_user"])}.jpg'
    if form.validate_on_submit():
        soubor = form.soubor.data
        typ_soubor_seznam = secure_filename(soubor.filename).split('.')
        typ_soubor = typ_soubor_seznam[1]
        nazev = f'{str(session["id_user"])}.{typ_soubor}'
        soubor.save(os.path.join(app.config['UPLOAD_FOLDER'], nazev))
    #obrazek = app.static_folder + f"/images/{nazev}"
    return render_template("foto.html", form = form, nazev = nazev)

if __name__ == '__main__':
    app.debug = True
    host = os.environ.get('IP', '127.0.0.1')
    port = int(os.environ.get('PORT', 8080))
    app.run(host=host, port=port)
