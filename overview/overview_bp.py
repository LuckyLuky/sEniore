from flask import (
    Blueprint,
    request,
    render_template,
    session,
    flash
   )
from flask_wtf import FlaskForm
from wtforms import RadioField
from dbaccess import DBAccess, DBUser
from flask_googlemaps import Map
from utils import GetImageUrl


blueprint = Blueprint("overview_bp", __name__, template_folder="templates")


class OverviewFormBase(FlaskForm):
    demandOffer = RadioField(
        "Nabídka/Poptávka", choices=[("2", "hledám nabídku"), ("1", "hledám poptávku")], default="2"
    )


@blueprint.route("/prehled", methods=["POST", "GET"])
def prehled_filtr():
    form = OverviewFormBase()
    services = DBAccess.ExecuteSQL("select * from services")
    addresses = DBAccess.ExecuteSQL("select distinct lower(town) from users")
    if request.method == "GET":
        return render_template(
            "prehled.html", form=form, services=services, addresses = addresses
        )

    elif request.method == "POST":
        vysledekselectu = DBAccess.ExecuteSQL(
            """
        SELECT u.first_name, u.surname, s.category, d.demand_offer, u.town, us.id, u.latitude, u.longitude, u.id, u.info
        FROM users u
        LEFT JOIN users_services us on us.id_users = u.id
        LEFT JOIN services s on s.id = us.id_services
        LEFT JOIN demand_offer d on d.id = us.id_demand_offer
        WHERE d.id = %s and s.id = %s and lower(u.town) = lower(%s)
        ORDER BY us.id desc
        """,
            (form.demandOffer.data, request.form["category"], request.form["address"])
        )
        if vysledekselectu is None:
            vysledekselectu = []

        dbUser = DBAccess.GetDBUserById(session['id_user'])

        if len(vysledekselectu) == 0:
          flash("Bohužel pro vámi zadanou kombinaci pro vás nemáme parťáka.") 


        # markery pro kazdeho vyhledaneho
        markers = []
        marker = {}
        marker["icon"] = "http://maps.google.com/mapfiles/kml/pal2/icon10.png"
        marker["lat"] = str(dbUser.latitude)
        marker["lng"] =  str(dbUser.longitude)
        marker["infobox"] = f'<b>{dbUser.first_name} {dbUser.surname}</b><br>{dbUser.info}<img class=img_mapa src= {GetImageUrl(dbUser.id)} />'
        markers.append(marker)

        for user in vysledekselectu:
            pictureUrl = GetImageUrl(user[8])
            marker = {}
            marker["icon"] = "http://maps.google.com/mapfiles/ms/icons/green-dot.png"
            marker["lat"] = str(user[6])
            marker["lng"] =  str(user[7])
            marker["infobox"] = f'<b>{user[0]} {user[1]}</b><br>{user[9]}<img class=img_mapa src= {pictureUrl} /> <a href="/match?id={user[5]}">Kontaktovat</a>'
            markers.append(marker)

        map = Map(
                    identifier="sndmap",
                    lat=str(dbUser.latitude),
                    lng=str(dbUser.longitude),
                    markers=markers
                    )  # get map, zoom on location of actual user, insert markers from select, ie users who provide specific required service

        return render_template("prehled_success.html", entries=vysledekselectu, sndmap=map)


