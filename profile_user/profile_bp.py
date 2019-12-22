import os
from flask import current_app as app
from flask import (
    Blueprint,
    request,
    render_template,
    session,
    abort,
    redirect,
    url_for
    )
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    FileField,
    RadioField
)

from flask_wtf.file import FileRequired
from wtforms.validators import InputRequired, DataRequired
from wtforms.widgets import TextArea
from werkzeug.utils import secure_filename

from dbaccess import DBAccess
from flask_googlemaps import Map
from utils import GetImageUrl, LoginRequired, GetCoordinates, UploadImage
from dbaccess import DBAccess,DBUser

blueprint = Blueprint("profile_bp", __name__, template_folder="templates")

class OverviewFormBase(FlaskForm):
    demandOffer = RadioField(
        "Nabídka/Poptávka", choices=[("2", "nabídka"), ("1", "poptávka")], default="2"
    )

class ProfilUpdateForm(FlaskForm):
    first_name = StringField( validators=[DataRequired()])
    surname = StringField( validators=[DataRequired()])
    telephone = StringField( validators=[DataRequired()])
    street = StringField( validators=[DataRequired()])
    street_number = StringField( validators=[DataRequired()])
    town = StringField( validators=[DataRequired()])
    post_code = StringField( validators=[DataRequired()])
    info = StringField(u'Napište krátký komentář:', widget=TextArea(), validators=[DataRequired()])
    soubor = FileField("Vlož obrázek")
    submit = SubmitField('Změnit údaje',render_kw=dict(class_="btn btn-outline-primary btn-block"))

@blueprint.route("/profil", methods=["GET", "POST"])
@LoginRequired()
def profil():
    dbUser = DBAccess.GetDBUserById(session["id_user"])
    name = f'{dbUser.first_name} {dbUser.surname}'
    info = dbUser.info
    mail = dbUser.email
    phone = dbUser.telephone
    latitude = str(
        DBAccess.ExecuteScalar(
            "select latitude from users where id = %s", (session["id_user"],)
        )
    )
    longitude = str(
        DBAccess.ExecuteScalar(
            "select longitude from users where id = %s", (session["id_user"],)
        )
    )
    username = session["user"]
    imgCloudUrl = GetImageUrl(session["id_user"])

    if request.method == "GET":
        users_services = DBAccess.ExecuteSQL(
            "select s.category as category, d.demand_offer as demand_offer,us.id from users_services us"
            " left join users u on us.id_users = u.id"
            " left join services s on s.id = us.id_services"
            " left join demand_offer d on d.id = us.id_demand_offer where u.id = %s",
            (session["id_user"],)
        )
        if(users_services is None):
            users_services = []

        sndmap = Map(
            identifier="sndmap",
            style="height:100%;width:100%;margin:0;",
            lat=latitude,
            lng=longitude,
            report_clickpos=True,
            clickpos_uri="/clickpost/",
            markers=[
                {
                    "icon": "http://maps.google.com/mapfiles/kml/pal2/icon10.png",
                    "lat": latitude,
                    "lng": longitude,
                    "infobox": f"<b>{username}</b><img class=img_mapa src= {imgCloudUrl} />"
                }
            ]
        )

        requests = DBAccess.ExecuteSQL(
            """select
              ud.first_name,
              ud.surname,
              ud.email,
              ud.telephone,
              uo.first_name,
              uo.surname,
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
            inner join requests_status rs on r.id_requests_status = rs.id
            where ud.id = %s or uo.id =%s """, (session["id_user"], session["id_user"])
        )
        if requests == None:
          requests = []
    
    return render_template(
        "profil.html", users_services=users_services, nazev=imgCloudUrl, sndmap=sndmap, requests = requests, name = name, info = info, mail = mail, phone = phone,
    )

@blueprint.route("/user_request_overview")
def user_request_overview():
  requests = DBAccess.ExecuteSQL(
            """select
              ud.first_name,
              ud.surname,
              ud.email,
              ud.telephone,
              uo.first_name,
              uo.surname,
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
            inner join requests_status rs on r.id_requests_status = rs.id
            where ud.id = %s or uo.id =%s """, (session["id_user"], session["id_user"])
        )
  if requests == None:
     requests = []

  return render_template("user_request_overview.html", requests = requests)

@LoginRequired()
@blueprint.route("/remove_service")
def remove_service():
    id = request.args.get("id", type=int)
    #check if there was argument
    if(id is None):
         abort(403)
    #check if service belongs to logged user..
    dbUser = DBUser.LoadFromSession('dbUser')
    user_service = DBAccess.ExecuteScalar("select id from users_services where id = %s and id_users=%s",(id,dbUser.id))
    if(user_service is None):
        abort(403)
    
    #delete service
    DBAccess.ExecuteUpdate("delete from users_services where id=%s", (id,))
    return redirect(url_for("profile_bp.profil"))

@LoginRequired()
@blueprint.route("/profil_editace",methods=["GET", "POST"])
def profil_editace():
   
    regForm = ProfilUpdateForm()
    dbUser = DBUser.LoadFromSession('dbUser')
    if(regForm.validate_on_submit()):
        dbUser.first_name = regForm.first_name.data
        dbUser.surname = regForm.surname.data
        dbUser.telephone = regForm.telephone.data
        dbUser.street = regForm.street.data
        dbUser.street_number = regForm.street_number.data
        dbUser.post_code = regForm.post_code.data
        dbUser.town = regForm.town.data
        dbUser.info = regForm.info.data

        address = "{} {} {} {}".format(dbUser.street, dbUser.street_number, dbUser.town, dbUser.post_code)
        coordinates = GetCoordinates(address)
        if(coordinates is not None):
            dbUser.latitude = coordinates[0]
            dbUser.longitude = coordinates[1]
        else:
            flash('Nenalezeny souřadnice pro vaši adresu',FlashStyle.Danger)
            return render_template("profil_editace.html", form = regForm)
        
        dbUser.UpdateDB()
        dbUser.SaveToSession('dbUser')

        if(regForm.soubor.data is not None and regForm.soubor.data != ''):
            file_name = secure_filename(regForm.soubor.data.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"],file_name)
            regForm.soubor.data.save(path)
            UploadImage(path,str(dbUser.id))

        return redirect(url_for('profile_bp.profil'))

        

    
    regForm.first_name.data = dbUser.first_name
    regForm.surname.data = dbUser.surname
    regForm.telephone.data = dbUser.telephone
    regForm.street.data = dbUser.street
    regForm.street_number.data = dbUser.street_number
    regForm.post_code.data = dbUser.post_code
    regForm.town.data = dbUser.town
    regForm.info.data = dbUser.info

    #if(regForm.validate_on_submit()):

    

    return render_template("profil_editace.html",form = regForm)



