import os
from flask import (
    Blueprint,
    request,
    url_for,
    render_template,
    redirect,
    session,
    flash,
)
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    FileField,
)
from flask_wtf.file import FileRequired
from wtforms.validators import InputRequired
from werkzeug.utils import secure_filename
from dbaccess import DBAccess
import hashlib
from flask import current_app as app
from utils import GetCoordinates, UploadImage


blueprint = Blueprint("login_bp", __name__, template_folder="templates")


class LoginForm(FlaskForm):
    user = StringField(
        "Uživatel", validators=[InputRequired()], render_kw=dict(class_="form-control")
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
            flash("Uživatel nenalezen")
            return render_template("login.html", form=form)

        userRow = userRow[
            0
        ]
        # execute sql gets list with one item, ie:[(email, password, first_name,
        # surname, id)], we need just (), ie tuple
        salt = userRow[6]

        def addSalt(passwordArg):
            return passwordArg + salt

        md5Pass = hashlib.md5(addSalt(str(form.password.data)).encode()).hexdigest()
        if userRow[1] != md5Pass:  # check if second item is equal to hashed password
            flash("Špatné heslo")
            return render_template("login.html", form=form)

        if userRow[5] == 0:
            flash(
                "Uživatel není ověřen, počkejte prosím na ověření"
                " administrátorem stránek."
            )
            return render_template("login.html", form=form)

        session["user"] = user
        session["id_user"] = userRow[4]
        session["level_user"] = userRow[5]
        flash("Uživatel/ka {0} {1} přihlášen/a".format(userRow[2], userRow[3]))
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


@blueprint.route("/registrace")
def registrace():
    return render_template("registrace.html")


@blueprint.route("/add_name", methods=["POST"])
def add_name():
    kwargs = {
        "first_name": request.form["first_name"],
        "surname": request.form["surname"],
        "email": request.form["email"],
        # "address": request.form["address"],
        "town": request.form["town"],
        "street": request.form["street"],
        "streetNumber": request.form["streetNumber"],
        "postCode": request.form["postCode"],
        "telephone": request.form["telephone"],
        "password": request.form["password"],
    }

    address = "{} {} {} {}".format(
        kwargs["street"], kwargs["streetNumber"], kwargs["town"], kwargs["postCode"]
    )
    
    coordinates = GetCoordinates(address)

    unique_number_users_long = DBAccess.ExecuteSQL("SELECT nextval('users_id_seq')")
    unique_number_users = unique_number_users_long[0]
    salt = DBAccess.ExecuteScalar("select salt()")
    DBAccess.ExecuteInsert(
        """insert into users (id, first_name, surname, email, street,
        streetNumber, town, postCode, telephone, password, salt,
        level, latitude,longitude)
     values (%s, %s, %s, %s, %s, %s,%s, %s, %s, md5(%s),%s,%s, %s, %s)""",
        (
            unique_number_users,
            request.form["first_name"],
            request.form["surname"],
            request.form["email"],
            request.form["street"],
            request.form["streetNumber"],
            request.form["town"],
            request.form["postCode"],
            request.form["telephone"],
            request.form["password"] + salt,
            salt,
            1,
            coordinates[0],
            coordinates[1]
        )
    )
    user = request.form["email"]
    userRow = DBAccess.ExecuteSQL(
        "select email, password, first_name, surname, id, level,salt from users "
        "where email like %s",
        (user,)
    )
    userRow = userRow[0]
    session["id_user"] = userRow[4]
    return render_template("/registrace_success.html", **kwargs)


@blueprint.route("/registrace_2/", methods=["GET", "POST"])
def photo():
    form = FileFormular()
    nazev = f'{str(session["id_user"])}.jpg'
    if form.validate_on_submit():
        soubor = form.soubor.data
        typ_soubor_seznam = secure_filename(soubor.filename).split(".")
        typ_soubor = typ_soubor_seznam[1]
        nazev = f'{str(session["id_user"])}.{typ_soubor}'

        soubor.save(os.path.join(app.config["UPLOAD_FOLDER"], nazev))
        UploadImage(os.path.join(app.config['UPLOAD_FOLDER'], nazev))

        flash("Foto uloženo, přihlaste se, prosím.")
        return redirect(url_for("login_bp.login"))
    return render_template("/registrace_2.html", form=form)
