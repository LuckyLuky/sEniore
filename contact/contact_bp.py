import os
from flask import (
    Blueprint,
    request,
    render_template,
    session,
    )
from dbaccess import DBAccess, DBUser
import configparser
import sendgrid
from datetime import datetime
from datetime import date, timedelta
from utils import SendMail,GetEmail, LoginRequired, getEmailAPIKey


blueprint = Blueprint("contact_bp", __name__, template_folder="templates")


@blueprint.route("/match/", methods=["GET"])
@LoginRequired()
def match():
    id_users_services = request.args.get("id", type=int)
    user_service_requested = DBAccess.ExecuteSQL(
        """
      SELECT d.demand_offer, s.category,d.id,u.id
      FROM users u
      LEFT JOIN users_services us on us.id_users = u.id
      LEFT JOIN services s on s.id = us.id_services
      LEFT JOIN demand_offer d on d.id = us.id_demand_offer
      WHERE us.id = %s
      """,
        (id_users_services,),
    )[0]

    demand_offer_text = 'poptává' if user_service_requested[2]==1 else 'nabízí'

    tomorrowStr = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')

    dbUser = DBAccess.GetDBUserById(user_service_requested[3])
    headerText = f'{dbUser.first_name} {dbUser.surname} {demand_offer_text} činnost {user_service_requested[1]}'

      
    kwargs = {
        "demand_offer": user_service_requested[0],
        "id_demand_offer": user_service_requested[2],
        "services": user_service_requested[1],
        "id": id_users_services,
        "headerText" : headerText
    }
    return render_template("/match.html", **kwargs)


@blueprint.route("/email_sent/", methods=["POST"])
@LoginRequired()
def email_sent():

    # kdo oslovuje
    user = session["user"]
    id_users_services = request.form.get("id", type=int)
    dbUser = DBUser.LoadFromSession('dbUser')
    email_oslovujici = dbUser.email
    name_oslovujici = dbUser.first_name
    surname_oslovujici = dbUser.surname
    # date = request.form.get("date", type=str)
    # time = request.form.get("time", type=str)
    # strDateTime = f"{date} {time}"
    # dt = datetime.strptime(strDateTime, "%Y-%m-%d %H:%M")

    info = request.form.get("info", type=str)

    email_user_long = DBAccess.ExecuteSQL(
    """
    SELECT u.email, u.id, s.id, d.id
    FROM users u
    LEFT JOIN users_services us on us.id_users = u.id
    LEFT JOIN services s on s.id = us.id_services
    LEFT JOIN demand_offer d on d.id = us.id_demand_offer
    WHERE us.id = %s
    """,(id_users_services,))

    email_user = email_user_long[0][0] # for testing emails are sent to admin
    services_id = email_user_long[0][2]
    id_demand_offer = email_user_long[0][3]

    offeringUserId = email_user_long[0][1] if id_demand_offer == 2 else session["id_user"]
    demandingUserId = email_user_long[0][1] if id_demand_offer == 1 else session["id_user"]



    id_request = DBAccess.GetSequencerNextVal("requests_id_seq")
    DBAccess.ExecuteInsert(
        "INSERT INTO requests (id, id_users_demand, id_users_offer, id_services, "
        "timestamp, date_time, add_information, id_requests_status, id_users_creator)"
        " values (%s, %s,%s,%s,now(),now(),%s,%s, %s)",
        (id_request, demandingUserId, offeringUserId, services_id, info, 1, session["id_user"])
    )

    # protistrana, kdo je osloven - email_user
    dbUser_protistrana = DBAccess.GetDBUserByEmail(email_user)
    name_protistrana = dbUser_protistrana.first_name
    surname_protistrana = dbUser_protistrana.surname

    

    

    text1 = 'Vaši nabídku' if id_demand_offer == 1 else 'Váš požadavek'

    text2 = 'Vaši nabídky' if id_demand_offer == 1 else 'vašeho požadavku'

    # mail to person who click on "contact"
    SendMail(GetEmail('noreplyMail'), f'{email_oslovujici}', 'Zaregistrována žádost o spolupráci', f'''<html>Úspěšně jsme zaregistrovali Vaší žádost o spolupráci. <br> 
    Váš kontakt je {name_protistrana},  email: {email_user} <br>
    Prosíme, spojte se, abyste se mohli domluvit na podrobnostech. Nezapomeňte dodržovat pravidla: <a href="https://app.seniore.org/podminky_dobrovolnici"> dobrovolníci</a> / <a href="https://app.seniore.org/podminky_seniori"> senioři</a><br>
    V případě potíží, nebo nejasností nám neváhejte napsat na contact@seniore.org. <br>
    Děkujeme, Váš tým Seniore</html>''')
    # mail to person who is being contacted
    SendMail(GetEmail('noreplyMail'), f'{email_user}', 'Zaregistrována žádost o spolupráci', f'''
    <html> Pan / paní {name_oslovujici} by se s Vámi rád/a spojil/a ohledně možné pomoci. 
    Kontaktní email je: {email_oslovujici} <br> 
    Prosíme, spojte se, abyste se mohli domluvit na podrobnostech. Nezapomeňte dodržovat pravidla: <a href="https://app.seniore.org/podminky_dobrovolnici"> dobrovolníci</a> / <a href="https://app.seniore.org/podminky_seniori"> senioři</a><br>
    V případě potíží, nebo nejasností nám neváhejte napsat na contact@seniore.org. <br>
    Děkujeme, Váš tým Seniore < / html > ''')
    # mail to admins
    SendMail(GetEmail('noreplyMail'), GetEmail('adminMail'), 'Seniore - zažádáno o spolupráci',
    f'''Uživatel {user} se s chce setkat s {email_user}! :-D <br>
    Doplňující informace: {info}. <br>
    Prosím, zkontrolujte žádost v http://seniore.herokuapp.com/requests_detail?id={id_request}.''')
    # print(response.status_code)
    # print(response.body)
    # print(response.headers)
    return render_template("email_sent.html", text1=text1, text2 =text2)
