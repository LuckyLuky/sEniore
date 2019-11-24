import os
from flask import (
    Blueprint,
    request,
    url_for,
    render_template,
    redirect,
    session,
    
)
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    FileField,
)
from flask_wtf.file import FileRequired
from wtforms.validators import InputRequired, DataRequired
from wtforms.widgets import TextArea
from werkzeug.utils import secure_filename
from dbaccess import DBAccess,DBUser
import hashlib
from flask import current_app as app
from utils import GetCoordinates, UploadImage, SendMail, GetImageUrl, LoginRequired, FlashStyle,flash
from lookup import AdminMail


blueprint = Blueprint("login_bp", __name__, template_folder="templates")

class RegistrationForm(FlaskForm):
    first_name = StringField( validators=[InputRequired()])
    surname = StringField( validators=[InputRequired()])
    email = StringField( validators=[InputRequired()])
    telephone = StringField( validators=[InputRequired()])
    street = StringField( validators=[InputRequired()])
    street_number = StringField( validators=[InputRequired()])
    town = StringField( validators=[InputRequired()])
    post_code = StringField( validators=[InputRequired()])
    password = PasswordField( validators=[InputRequired()])
    submit = SubmitField('Pokračovat dále',render_kw=dict(class_="btn btn-outline-primary btn-block"))


class LoginForm(FlaskForm):
    user = StringField(
        "Přihlašovací jméno", validators=[InputRequired()], render_kw=dict(class_="form-control")
    )  # Přihlašovací jméno
    password = PasswordField(
        "Heslo", validators=[InputRequired()], render_kw=dict(class_="form-control")
    )  # Heslo
    submit = SubmitField(
        "Odeslat", render_kw=dict(class_="btn btn-outline-primary btn-block")
    )


class FileFormular(FlaskForm):
    soubor = FileField("Vlož obrázek", validators=[FileRequired()])
    submit = SubmitField(
        "Odeslat", render_kw=dict(class_="btn btn-outline-primary btn-block")
    )


class TextFormular(FlaskForm):
    comment = StringField(u'Napište krátký komentář:', widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField(
      "Dokončit registraci", render_kw=dict(class_="btn btn-outline-primary btn-block")
    )


@blueprint.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.user.data
        userRow = DBAccess.ExecuteSQL(
            "select email, password, first_name, surname, id, level,salt from "
            "users where email like %s",
            (user,),
        )

        if userRow is None:
            flash("Uživatel nenalezen",FlashStyle.Danger)
            return render_template("login.html", form=form)

        userRow = userRow[0]
        # execute sql gets list with one item, ie:[(email, password, first_name,
        # surname, id)], we need just (), ie tuple
        salt = userRow[6]

        def addSalt(passwordArg):
            return passwordArg + salt

        md5Pass = hashlib.md5(addSalt(str(form.password.data)).encode()).hexdigest()
        if userRow[1] != md5Pass:  # check if second item is equal to hashed password
            flash("Špatné heslo",FlashStyle.Danger)
            return render_template("login.html", form=form)

        if userRow[5] == 0:
            flash(
                "Uživatel není ověřen, počkejte prosím na ověření"
                " administrátorem stránek.", FlashStyle.Danger
            )
            return render_template("login.html", form=form)

        session["user"] = user
        session["id_user"] = userRow[4]
        session["level_user"] = userRow[5]
        dbUser = DBAccess.GetDBUserById(userRow[4])
        dbUser.SaveToSession('dbUser')
        flash("Uživatel/ka {0} {1} přihlášen/a".format(userRow[2], userRow[3]), FlashStyle.Success)
        return redirect(url_for("profile_bp.profil"))
    return render_template("login.html", form=form)


@blueprint.route("/logout/", methods=["GET", "POST"])
def odhlasit():
    # session.pop("user", None)
    # session.pop("id_user", None)
    # session.pop("level_user",None)
    session.clear()
    return redirect(url_for("login_bp.login"))


@blueprint.route("/")
def index():
    return render_template("layout.html")


@blueprint.route("/registrace", methods=["GET", "POST"])
def registrace():
    form = RegistrationForm()
    if(form.validate_on_submit()):
        dbUser = DBUser()
        dbUser.email = form.email.data
        dbUser.password = form.password.data
        dbUser.first_name = form.first_name.data
        dbUser.surname = form.surname.data
        dbUser.telephone = form.telephone.data
        dbUser.town = form.town.data
        dbUser.street = form.street.data
        dbUser.street_number = form.street_number.data
        dbUser.post_code = form.post_code.data
        dbUser.level = 2 # for testing, then set to 0 for manual verifivation of user's pohoto, ...


        if DBAccess.ExecuteScalar('select id from users where email=%s',(dbUser.email,)) is not None:
          flash(f'Uživatel {dbUser.email} je již zaregistrován, zvolte jiný email.',FlashStyle.Danger)
          dbUser.email = None
          form.email.data = None
          return render_template("registrace.html", form = form)


        dbUser.salt = salt = DBAccess.ExecuteScalar("select salt()")

        #md% tranform password use md5 function on password + salt
        md5Pass = hashlib.md5((dbUser.password+dbUser.salt).encode()).hexdigest()
        dbUser.password = md5Pass
        
        

        kwargs = dbUser.__dict__
        address = "{} {} {} {}".format(kwargs["street"], kwargs["street_number"], kwargs["town"], kwargs["post_code"])
        coordinates = GetCoordinates(address)
        if(coordinates is not None):
            dbUser.latitude = coordinates[0]
            dbUser.longitude = coordinates[1]
        else:
            flash('Nenalezeny souřadnice pro vaši adresu',FlashStyle.Danger)
            return render_template("registrace.html", form = form)


        dbUser.SaveToSession('dbUserRegistration')
        return render_template("/registrace_success.html", **kwargs)
    return render_template("registrace.html", form = form)


# @blueprint.route("/add_name", methods=["POST"])
# def add_name():
#     kwargs = {
#         "first_name": request.form["first_name"],
#         "surname": request.form["surname"],
#         "email": request.form["email"],
#         # "address": request.form["address"],
#         "town": request.form["town"],
#         "street": request.form["street"],
#         "streetNumber": request.form["streetNumber"],
#         "postCode": request.form["postCode"],
#         "telephone": request.form["telephone"],
#         "password": request.form["password"],
#     }

#     address = "{} {} {} {}".format(
#         kwargs["street"], kwargs["streetNumber"], kwargs["town"], kwargs["postCode"]
#     )
    
#     coordinates = GetCoordinates(address)

#     unique_number_users_long = DBAccess.ExecuteSQL("SELECT nextval('users_id_seq')")
#     unique_number_users = unique_number_users_long[0]
#     salt = DBAccess.ExecuteScalar("select salt()")
#     DBAccess.ExecuteInsert(
#         """insert into users (id, first_name, surname, email, street,
#         streetNumber, town, postCode, telephone, password, salt,
#         level, latitude,longitude)
#      values (%s, %s, %s, %s, %s, %s,%s, %s, %s, md5(%s),%s,%s, %s, %s)""",
#         (
#             unique_number_users,
#             request.form["first_name"],
#             request.form["surname"],
#             request.form["email"],
#             request.form["street"],
#             request.form["streetNumber"],
#             request.form["town"],
#             request.form["postCode"],
#             request.form["telephone"],
#             request.form["password"] + salt,
#             salt,
#             1,
#             coordinates[0],
#             coordinates[1]
#         )
#     )
#     user = request.form["email"]
#     userRow = DBAccess.ExecuteSQL(
#         "select email, password, first_name, surname, id, level,salt from users "
#         "where email like %s",
#         (user,)
#     )
#     userRow = userRow[0]
#     session["id_user"] = userRow[4]
#     return render_template("/registrace_success.html", **kwargs)


@blueprint.route("/registrace_photo/", methods=["GET", "POST"])
def photo():
    form = FileFormular()
    if form.validate_on_submit():
        file_name = secure_filename(form.soubor.data.filename)
        session['fotoPath'] = os.path.join(app.config["UPLOAD_FOLDER"],file_name)
        form.soubor.data.save(session['fotoPath'])
        flash("Foto nahráno, jsme u posledního kroku registrace :-) ", FlashStyle.Success)
        return redirect(url_for("login_bp.comment"))
    return render_template("/registrace_photo.html", form=form)


@blueprint.route("/registraceComment/", methods=["GET", "POST"])
def comment():
    form = TextFormular()
    if form.validate_on_submit():
        dbUser = DBUser.LoadFromSession('dbUserRegistration')
        dbUser.info = form.comment.data
        dbUser.id = DBAccess.GetSequencerNextVal('users_id_seq')
        dbUser.InsertDB()
        UploadImage(session['fotoPath'],str(dbUser.id))
        SendMail('noreply@seniore.org', AdminMail["kacka"],'Zaregistrován nový uživatel',f'<html>Nový uživatel zaregistrovan, čeká na ověření. <br> <img src={GetImageUrl(dbUser.id)}>foto</img> <br> údaje: {dbUser.__dict__}')
        flash(f'Registrace uživatele {dbUser.first_name} {dbUser.surname} úspěšně dokončena. Váš profil nyní musíme zkontrolovat. Zabere nám to zhruba 5 až 7 dní. Prosíme, mějte strpení. Ruční ověřování považujeme za nezbytnost kvůli bezpečnosti. Ozveme se Vám telefonicky. POZN: Nyní se lze pro testovací účely přihlásit rovnou ;-)', FlashStyle.Success)
        return redirect(url_for("login_bp.login"))
    return render_template("/registraceComment.html", form=form)


@blueprint.route("/goodpracticephoto")
def photo_good_practice():
    return render_template("goodpracticephoto.html")