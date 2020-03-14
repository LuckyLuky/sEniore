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
    # note that we set the 404 status explicitly
    return render_template('403bat.html'), 403

@app.errorhandler(Exception)
def handle_exception(e):
    #Return JSON instead of HTML for HTTP errors
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    text = f'{response.data}'
    to_emails = [(AdminMail['kacka']), (AdminMail['oodoow'])]
    SendMail('noreply@seniore.org', to_emails, 'Error on app.seniore.org', text)   
    return response


if __name__ == "__main__":
    app.debug = True
    host = os.environ.get("IP", "127.0.0.1")
    port = int(os.environ.get("PORT", 8080))
    app.run(host=host, port=port)
