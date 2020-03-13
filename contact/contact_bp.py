import os
from flask import (
    Blueprint,
    request,
    render_template,
    session,
    )
from dbaccess import DBAccess
import configparser
import sendgrid
from datetime import datetime
from lookup import AdminMail
from datetime import date, timedelta


blueprint = Blueprint("contact_bp", __name__, template_folder="templates")


@blueprint.route("/match/", methods=["GET"])
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


def getEmailAPIKey():
    API_Key = os.environ.get("SENDGRID_API_KEY")
    if not API_Key:
        configParser = configparser.RawConfigParser()
        configFilePath = r"config.txt"
        configParser.read(configFilePath)
        API_Key = configParser.get("my-config", "sendgrid_api_key")
    if not API_Key:
        raise Exception("Could not find API_Key value.")
    return API_Key


@blueprint.route("/email_sent/", methods=["POST"])
def email_sent():
    user = session["user"]
    id_users_services = request.form.get("id", type=int)
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

    message = {
        "personalizations": [
            {"to": [{"email": AdminMail["kacka"]}], "subject": "Seniore"}
        ],
        "from": {"email": "noreply@seniore.org"},
        "content": [
            {
                "type": "text/plain",
                "value": f"Uživatel {user} se s chce setkat s {email_user}.Doplňující informace: {info}. Prosím, zkontrolujte žádost v http://seniore.herokuapp.com/requests_detail?id={id_request}.",
            }
        ],
    }

    text1 = 'Vaši nabídku' if id_demand_offer == 1 else 'Váš požadavek'

    text2 = 'vaší nabídky' if id_demand_offer == 1 else 'vašeho požadavku'


    sg = sendgrid.SendGridAPIClient(getEmailAPIKey())

    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
    return render_template("email_sent.html", text1=text1, text2 =text2)
