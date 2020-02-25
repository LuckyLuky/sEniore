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
from utils import GetImageUrl, RenameImage, UploadImage, DeleteImage, LoginRequired, GetCoordinates,  SendMail, flash, FlashStyle
from dbaccess import DBAccess,DBUser
from lookup import AdminMail
from itsdangerous import URLSafeTimedSerializer
from login.login_bp import TextFormular

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
              to_char(r.date_time, 'DD-MM-YYYY HH24:MI'),
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
            """select s.category,

            case when	ud.id = %s
            then 	'Přijímám' 
            else 	'Pomáhám'
            end,

            case when 	ud.id = %s
            then	uo.first_name 
            else	ud.first_name
            end,
            
            case when 	ud.id = %s
            then	uo.surname 
            else	ud.surname
            end,

            to_char(r.date_time, 'DD-MM-YYYY HH24:MI'),
            rs.status,
            r.id
            from requests r
            inner join services s on r.id_services = s.id
            inner join users ud on r.id_users_demand = ud.id
            inner join users uo on r.id_users_offer = uo.id
            inner join requests_status rs on r.id_requests_status = rs.id
            where ud.id = %s or uo.id = %s  order by r.date_time desc""", (session["id_user"], session["id_user"],session["id_user"],session["id_user"],    session["id_user"])
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

        if(regForm.soubor.data is not None and regForm.soubor.data.filename != ''):
            file_name = secure_filename(regForm.soubor.data.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"],file_name)
            regForm.soubor.data.save(path)
            json = UploadImage(path,str(dbUser.id)+'new')
            version = json['version']
            newImageUrl = GetImageUrl(str(dbUser.id) + 'new', version = version)

            ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])
            token = ts.dumps(dbUser.email, salt='change-photo-key')
            confirm_url = url_for(
                'profile_bp.change_photo_confirm',
                token=token,
                _external=True)
            
            denied_url = url_for(
                'profile_bp.change_photo_denied',
                token=token,
                _external=True)
            noCacheSufix = '?nocache=<?php echo time(); ?'

            email_text = f'''Uživatel { dbUser.first_name } {dbUser.surname} {dbUser.email} si změnil profilovou fotografii.  <br>\
                 <img src={GetImageUrl(dbUser.id)+noCacheSufix}>původní foto</img> <br>\
                 <img src={newImageUrl+noCacheSufix}>nové foto</img> <br>\
                Link pro schválení fotografie {confirm_url} <br>\
                Link pro odmítnutí fotografie {denied_url}'''

            to_emails = [(AdminMail['kacka']), (AdminMail['oodoow']), (AdminMail['michal'])]

            SendMail("noreply@seniore.cz",to_emails,'Seniore.cz - schválení profilové fotografie',email_text)
            flash("Nová profilová fotografie byla odeslána administrátorovi ke schválení, o výsledku budete informováni emailem.",FlashStyle.Success)
        return redirect(url_for('profile_bp.profil'))
   
    regForm.first_name.data = dbUser.first_name
    regForm.surname.data = dbUser.surname
    regForm.telephone.data = dbUser.telephone
    regForm.street.data = dbUser.street
    regForm.street_number.data = dbUser.street_number
    regForm.post_code.data = dbUser.post_code
    regForm.town.data = dbUser.town
    regForm.info.data = dbUser.info
    return render_template("profil_editace.html",form = regForm)

@LoginRequired()
@blueprint.route("/change_photo_confirm/<token>",methods=["GET", "POST"])
def change_photo_confirm(token):
    try:
        ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        email = ts.loads(token, salt="change-photo-key")
    except:
        abort(403)
    dbUser = DBAccess.GetDBUserByEmail(email)
    RenameImage(str(dbUser.id)+'new',str(dbUser.id))
    DeleteImage(str(dbUser.id)+'new')

    SendMail('noreply@seniore.org',dbUser.email,"Seniore.org - schválení profilové fotografie","Vaše nové profilové foto na seniore.org bylo schváleno a bude nahráno na váš profil.")
    return render_template('photo_confirmation.html',denied = False, text = f'Nové profilové foto nahráno, informační mail odeslán uživateli {email}')

@LoginRequired()
@blueprint.route("/change_photo_denied/<token>",methods=["GET", "POST"])
def change_photo_denied(token):
    try:
        ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        email = ts.loads(token, salt="change-photo-key")
    except:
        abort(403)

    form = TextFormular()

    if(form.validate_on_submit()):
        dbUser = DBAccess.GetDBUserByEmail(email)
        SendMail('noreply@seniore.org',dbUser.email,"Seniore.org - schválení profilové fotografie",f'Vaše nové profilové foto na seniore.org bylo zamístnuto, důvod zamítnutí: <br> {form.comment.data}')
        DeleteImage(str(dbUser.id)+'new')
        text = f'Informační email o zamítnutí byl odeslán uživateli {email} a nová fotografie smazána.'
        return render_template('photo_confirmation.html', denied = False, text = text)

    form.comment.label.text = 'Napište důvod zamítnutí'
    form.submit.label.text  = 'Odeslat mail'
    text = f'Nové profilové foto zamítnuto, vyplňte důvod odmítnutí a odešlete informační mail uživateli {email}'
    return render_template('photo_confirmation.html',denied = True, text = text, form=form)





