import os
from flask import (
    Blueprint,
    request,
    url_for,
    render_template,
    redirect,
    session,
    abort
    
)
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    FileField,
)
from flask_wtf.file import FileRequired
from wtforms.validators import InputRequired, DataRequired, Length
from wtforms.widgets import TextArea
from werkzeug.utils import secure_filename
from dbaccess import DBAccess,DBUser
import hashlib
from flask import current_app as app
from utils import GetCoordinates, UploadImage, SendMail, GetImageUrl, LoginRequired, FlashStyle,flash, SendMail
from lookup import AdminMail
from itsdangerous import URLSafeTimedSerializer
from flask_bcrypt import Bcrypt



blueprint = Blueprint("login_bp", __name__, template_folder="templates")

class EmailForm(FlaskForm):
    email = StringField( validators=[InputRequired()])
    submit = SubmitField('Odeslat ověřovací email',render_kw=dict(class_="btn btn-outline-primary"))

class NewPasswordForm(FlaskForm):
    password = PasswordField( validators=[InputRequired()])
    passwordAgain = PasswordField( validators=[InputRequired()])
    submit = SubmitField('Nastavit nové heslo',render_kw=dict(class_="btn btn-outline-primary btn-block"))


class RegistrationForm(FlaskForm):
    # first_name = StringField( validators=[InputRequired()])
    # surname = StringField( validators=[InputRequired()])
    email = StringField( render_kw={'disabled':''})
    # telephone = StringField( validators=[InputRequired()])
    # street = StringField( validators=[InputRequired()])
    # street_number = StringField( validators=[InputRequired()])
    # town = StringField( validators=[InputRequired()])
    # post_code = StringField( validators=[InputRequired()])
    password = PasswordField( validators=[InputRequired()])
    passwordAgain = PasswordField( validators=[InputRequired()])
    submit = SubmitField('Pokračovat dále',render_kw=dict(class_="btn btn-outline-primary btn-block"))

class RegistrationFormName(FlaskForm):
    first_name = StringField( validators=[InputRequired()])
    surname = StringField( validators=[InputRequired()])
    telephone = StringField( validators=[InputRequired(), Length(min=9, max=9)], )
    submit = SubmitField('Pokračovat dále',render_kw=dict(class_="btn btn-outline-primary btn-block"))

class RegistrationFormAddress(FlaskForm):
    street = StringField( validators=[InputRequired()])
    street_number = StringField( validators=[InputRequired()])
    town = StringField( validators=[InputRequired()])
    post_code = StringField( validators=[InputRequired()])
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
        "Odeslat", render_kw=dict(class_="btn btn-outline-primary")
    )

class IDFormular(FlaskForm):
    soubor = FileField("Vlož fotku OP", validators=[FileRequired()])
    submit = SubmitField(
        "Odeslat", render_kw=dict(class_="btn btn-outline-primary")
    )

class TextFormular(FlaskForm):
    comment = StringField(u'Napište krátký komentář:', widget=TextArea(), validators=[DataRequired(),Length(max=500)])
    submit = SubmitField(
      "Dokončit registraci", render_kw=dict(class_="btn btn-outline-primary")
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

        #md5Pass = hashlib.md5(addSalt(str(form.password.data)).encode()).hexdigest()

        bcrypt = Bcrypt()
        #bcryptHash = bcrypt.generate_password_hash(addSalt(str(form.password.data)))

        # check if second item is equal to hashed password
        try:
            if  bcrypt.check_password_hash(userRow[1], form.password.data) == False:
                flash("Špatné heslo",FlashStyle.Danger)
                return render_template("login.html", form=form)
        except:
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
        # flash("Uživatel/ka {0} {1} přihlášen/a".format(userRow[2], userRow[3]), FlashStyle.Success)
        return redirect(url_for("overview_bp.prehled_all"))
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
    return redirect(url_for("login_bp.login"))


@blueprint.route("/registrace", methods=["GET", "POST"])
def registrace():
        
    form = RegistrationForm()
        
    if form.validate_on_submit():
        if(form.password.data!=form.passwordAgain.data):
            flash('Hesla nejsou stejná.',FlashStyle.Danger)
            email = session['confirmed_email']
            form.email.data = email
            return render_template("registrace.html", form = form)
        email = session['confirmed_email']
        form.email.data = email
        dbUser = DBUser()
        dbUser.email = form.email.data
        dbUser.password = form.password.data
        dbUser.level = 0

    
        if DBAccess.ExecuteScalar('select id from users where email=%s',(dbUser.email,)) is not None:
          flash(f'Uživatel {dbUser.email} je již zaregistrován, zvolte jiný email.',FlashStyle.Danger)
          dbUser.email = None
          form.email.data = None
          return render_template("registrace.html", form = form)


        dbUser.salt = salt = DBAccess.ExecuteScalar("select salt()")
        
        #md% tranform password use md5 function on password + salt
        # md5Pass = hashlib.md5((dbUser.password+dbUser.salt).encode()).hexdigest()
        # dbUser.password = md5Pass
        bcrypt = Bcrypt()
        dbUser.password = bcrypt.generate_password_hash(password).decode('UTF-8')



        
        dbUser.SaveToSession('dbUserRegistration')
        return redirect(url_for("login_bp.registrace_name"))
    
    #email = session.pop('confirmed_email',None)
    email = session['confirmed_email']

    if(email is None):
        abort(403)

    form.email.data = email
    
    return render_template("registrace.html", form = form)

@blueprint.route("/registrace_name", methods=["GET", "POST"])
def registrace_name():
        
    form = RegistrationFormName()
        
    if form.validate_on_submit():
        dbUser =  DBUser.LoadFromSession('dbUserRegistration')
        dbUser.first_name = form.first_name.data
        dbUser.surname = form.surname.data
        dbUser.telephone = form.telephone.data
            
        dbUser.SaveToSession('dbUserRegistration')
        return redirect(url_for("login_bp.registrace_address"))
    
    return render_template("registrace_name.html", form = form)


@blueprint.route("/registrace_address", methods=["GET", "POST"])
def registrace_address():
        
    form = RegistrationFormAddress()
        
    if form.validate_on_submit():
        dbUser =  DBUser.LoadFromSession('dbUserRegistration')
        dbUser.town = form.town.data
        dbUser.street = form.street.data
        dbUser.street_number = form.street_number.data
        dbUser.post_code = form.post_code.data
            
        kwargs = dbUser.__dict__
        address = "{} {} {} {}".format(kwargs["street"], kwargs["street_number"], kwargs["town"], kwargs["post_code"])
        coordinates = GetCoordinates(address)
        if(coordinates is not None):
            dbUser.latitude = coordinates[0]
            dbUser.longitude = coordinates[1]
        else:
            flash('Nenalezeny souřadnice pro vaši adresu',FlashStyle.Danger)
            return render_template("registrace_address.html", form = form)


        dbUser.SaveToSession('dbUserRegistration')
        return redirect(url_for("login_bp.photo"))
    
    return render_template("registrace_address.html", form = form)


@blueprint.route("/registrace_photo/", methods=["GET", "POST"])
def photo():
    form = FileFormular()
    if form.validate_on_submit():
        file_name = secure_filename(form.soubor.data.filename)
        session['fotoPath'] = os.path.join(app.config["UPLOAD_FOLDER"],file_name)
        form.soubor.data.save(session['fotoPath'])
        # flash("Foto nahráno, jsme u posledního kroku registrace :-) ", FlashStyle.Success)
        return redirect(url_for("login_bp.registrace_idCard"))
    return render_template("/registrace_photo.html", form=form)

@blueprint.route("/registrace_idCard/", methods=["GET", "POST"])
def registrace_idCard():
    form = IDFormular()
    if form.validate_on_submit():
        file_name = secure_filename(form.soubor.data.filename)
        session['idPath'] = os.path.join(app.config["UPLOAD_FOLDER"],file_name)
        form.soubor.data.save(session['idPath'])
        # flash("Foto nahráno, jsme u posledního kroku registrace :-) ", FlashStyle.Success)
        return redirect(url_for("login_bp.comment"))
    return render_template("/registrace_idCard.html", form=form)

@blueprint.route("/registraceComment/", methods=["GET", "POST"])
def comment():
    form = TextFormular()
    if form.validate_on_submit():
        dbUser = DBUser.LoadFromSession('dbUserRegistration')
        dbUser.info = form.comment.data
        dbUser.id = DBAccess.GetSequencerNextVal('users_id_seq')
        dbUser.InsertDB()
        UploadImage(session['fotoPath'],str(dbUser.id))
        UploadImage(session['idPath'],str(dbUser.id) + 'OP')
        OP_id = str(dbUser.id) + 'OP'

        ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        token = ts.dumps(dbUser.id, salt='email-confirm-key')
        confirm_url = url_for(
            'login_bp.user_confirmation',
            token=token,
            _external=True)



        SendMail('noreply@seniore.org', AdminMail["kacka"],'Zaregistrován nový uživatel',f'<html>Nový uživatel zaregistrovan, čeká na schválení. <br> <img src={GetImageUrl(dbUser.id)}>foto</img> <br> <img src={GetImageUrl(OP_id)}>OP</img> <br> údaje: {dbUser.__dict__} <br> Pro schválení uživatele klikněte na následující link {confirm_url}')
        flash(f'Registrace uživatele {dbUser.first_name} {dbUser.surname} úspěšně dokončena. Váš profil nyní musíme zkontrolovat. Zabere nám to zhruba 5 až 7 dní. Prosíme, mějte strpení. Ruční ověřování považujeme za nezbytnost kvůli bezpečnosti. O schválení vás budeme informovat emailem.', FlashStyle.Success)
        SendMail('noreply@seniore.org',dbUser.email,'Registrace na sEniore.org','Děkujeme za vaši registraci na sEniore.org. Váš profil nyní musíme zkontrolovat. Zabere nám to zhruba 5 až 7 dní. Prosíme, mějte strpení. Ruční ověřování považujeme za nezbytnost kvůli bezpečnosti. O schválení vás budeme informovat emailem. Děkujeme, tým sEniore.org')
        return redirect(url_for("login_bp.login"))
    return render_template("/registraceComment.html", form=form)


@blueprint.route("/goodpracticephoto")
def photo_good_practice():
    return render_template("goodpracticephoto.html")

@blueprint.route("/registrace_email",methods=["GET", "POST"])
def registration_email():
    emailForm = EmailForm()
    
    if emailForm.validate_on_submit():
      if request.form.getlist('conditionsAccept')!=['1', '2']:
        flash(f'Je potřeba souhlasit s podmínkami.',FlashStyle.Danger)
        return render_template("registrace_email.html", form = emailForm)
      if DBAccess.ExecuteScalar('select id from users where email=%s',(emailForm.email.data,)) is not None:
          flash(f'Uživatel {emailForm.email.data} je již zaregistrován, zvolte jiný email.',FlashStyle.Danger)
          emailForm.email.data = None
          return render_template("registrace_email.html", form = emailForm)
      else:
        ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        token = ts.dumps(emailForm.email.data, salt='email-confirm-key')
        confirm_url = url_for(
            'login_bp.email_confirmation',
            token=token,
            _external=True)
        email_text = f'Prosím klikněte na následující odkaz pro ověření vašeho emailu a pokračování v registraci.<br>Tento odkaz bude platný následujících 24 hodin.<br>{confirm_url}'
        SendMail("noreply@seniore.cz",emailForm.email.data,'Seniore.cz - ověření emailu',email_text)
        #flash("Na zadanou adresu byl odeslán email s odkazem na pokračování v registraci.",FlashStyle.Success)
        emailForm.submit.label.text = "Odeslat ověřovací email znovu"
        return render_template("registrace_email2.html", form = emailForm)
    return render_template("registrace_email.html", form = emailForm)

@blueprint.route("/email_confirmation/<token>")
def email_confirmation(token):
    try:
        ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)
    except:
        abort(403)
    session['confirmed_email'] = email
    return redirect(url_for('login_bp.registrace'),)

@blueprint.route("/user_confirmation/<token>")
def user_confirmation(token):
    try:
        ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        user_id = ts.loads(token, salt="email-confirm-key")
    except:
        abort(403)
    dbUser = DBAccess.GetDBUserById(user_id)
    DBAccess.ExecuteUpdate('update users set level=1 where id=%s', (user_id,))
    email_text = f'Dobrý den, váš účet byl ověřen a nyní se můžete nalogovat. :-)'
    SendMail("noreply@seniore.cz",dbUser.email,'Seniore.cz - ověření účtu',email_text)
        
    return f'Uživatel {dbUser.first_name} {dbUser.surname} byl nastaven jako schválený a byl mu odeslán informační email.'


@blueprint.route("/zapomenute_heslo",methods=["GET", "POST"])
def lost_password():
    emailForm = EmailForm()
    
    if emailForm.validate_on_submit():
        if DBAccess.ExecuteScalar('select id from users where email=%s',(emailForm.email.data,)) is None:
          flash(f'Uživatel {emailForm.email.data} nebyl nalezen, zvolte jiný email.',FlashStyle.Danger)
          emailForm.email.data = None
          return render_template("registrace_email.html", form = emailForm)
        else:
            ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])
            token = ts.dumps(emailForm.email.data, salt='email-renew-key')
            confirm_url = url_for(
                'login_bp.new_password',
                token=token,
                _external=True)
            email_text = f'Prosím klikněte na následující odkaz pro zadání nového hesla.<br>Tento odkaz bude platný následujících 24 hodin.<br>{confirm_url}'
            SendMail("noreply@seniore.cz",emailForm.email.data,'Seniore.cz - obnova zapomenutého hesla',email_text)
            flash("Na zadanou adresu byl odeslán email s odkazem na obnovu hesla.",FlashStyle.Success)
            emailForm.submit.label.text = "Odeslat email znovu"
            return render_template("lost_password.html", form = emailForm)
    return render_template("lost_password.html", form = emailForm)

@blueprint.route("/new_password/<token>",methods=["GET", "POST"])
def new_password(token):
    try:
        ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        email = ts.loads(token, salt="email-renew-key", max_age=86400)
    except:
        abort(403)
    form = NewPasswordForm()
    if(form.validate_on_submit()):
        if(form.password.data!=form.passwordAgain.data):
            flash('Hesla nejsou stejná.',FlashStyle.Danger)
            return render_template('new_password.html',form=form, email=email)
        #salt = DBAccess.ExecuteScalar("select salt()")
        #md5Pass = hashlib.md5((form.password.data+salt).encode()).hexdigest()
        bcrypt = Bcrypt()
        bcryptHash = bcrypt.generate_password_hash(form.password.data).decode('UTF -8')
        DBAccess.ExecuteUpdate('update users set password=%s where email like %s',(bcryptHash,email))
        flash('Nové heslo nastaveno, nyní se zkuste přihlásit.',FlashStyle.Success)
        return redirect(url_for('login_bp.login'),)
    return render_template('new_password.html',form=form, email=email)

@blueprint.route("/conditions_1")
def conditions_1():
    return render_template("conditions_1.html")

@blueprint.route("/conditions_2")
def conditions_2():
    return render_template("conditions_2.html")

