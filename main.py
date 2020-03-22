import os
from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from utils import getGoogleAPIKey, CloudinaryConfigure, getSecretKey
from login import login_bp
from profile_user import profile_bp
from serviceReg import serviceReg_bp
from overview import overview_bp
from contact import contact_bp
from request_user import request_bp
from flask import Flask
from flask_talisman import Talisman
from flask import json
from werkzeug.exceptions import HTTPException
from utils import SendMail
from lookup import AdminMail
import sys
import traceback


app = Flask("seniore")

talisman = Talisman(app, content_security_policy=None)

GoogleMaps(app, key=getGoogleAPIKey())


CloudinaryConfigure()

app.config["SECRET_KEY"] = getSecretKey()

UPLOAD_FOLDER = app.static_folder + "/users_images/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.register_blueprint(login_bp.blueprint)
app.register_blueprint(profile_bp.blueprint)
app.register_blueprint(serviceReg_bp.blueprint)
app.register_blueprint(overview_bp.blueprint)
app.register_blueprint(contact_bp.blueprint)
app.register_blueprint(request_bp.blueprint)


@app.errorhandler(403)
def page_not_authorized(e):
    return render_template('403bat.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_HTTP.html'), 404

@app.errorhandler(Exception)
def handle_exception(e):
        text = ''
        dbUser = DBUser.LoadFromSession('dbUser')
        if(dbUser != None):
            text+=f'Uzivatel:<br>{dbUser.__dict__}<br>'
        else:
            dbUserReg = DBUser.LoadFromSession('dbUserRegistration')
            if(dbUserReg != None):
                text+=f'Uzivatel registrace:<br>{dbUserReg.__dict__}<br>'

        etype, value, tb = sys.exc_info()
        exceptionString = '<br>'.join(traceback.format_exception(etype, value, tb))
        text += f'Error message:<br> {exceptionString}'
        to_emails = [(AdminMail['kacka']), (AdminMail['oodoow'])]
        SendMail('noreply@seniore.org', to_emails, 'Internal error on app.seniore.org', text)
        return render_template('error_500.html')
        



if __name__ == "__main__":
    app.debug = True
    host = os.environ.get("IP", "127.0.0.1")
    port = int(os.environ.get("PORT", 8080))
    app.run(host=host, port=port)
