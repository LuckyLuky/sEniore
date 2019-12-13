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
    RadioField,
    )
from dbaccess import DBAccess
from flask_googlemaps import Map
from utils import GetImageUrl, LoginRequired
from dbaccess import DBAccess,DBUser

blueprint = Blueprint("profile_bp", __name__, template_folder="templates")


class OverviewFormBase(FlaskForm):
    demandOffer = RadioField(
        "Nabídka/Poptávka", choices=[("2", "nabídka"), ("1", "poptávka")], default="2"
    )


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
            style="height:80%;width:80%;margin:0;",
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
        "profil.html", users_services=users_services, nazev=imgCloudUrl, sndmap=sndmap, requests = requests, name = name, info = info, mail = mail, phone = phone
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


