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
from serviceReg.serviceReg_bp import regFormBuilder


blueprint = Blueprint("overview_bp", __name__, template_folder="templates")


class OverviewFormBase(FlaskForm):
    demandOffer = RadioField(
        "Nabídka/Poptávka", choices=[("2", "hledám někoho, kdo nabízí"), ("1", "hledám někoho, kdo poptává")], default="2"
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
        marker["infobox"] = f'<b>{dbUser.first_name} </b><br>{dbUser.info}<img class=img_mapa src= {GetImageUrl(dbUser.id)} />'
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
                    style="height:100%;width:100%;margin:0;",
                    lat=str(dbUser.latitude),
                    lng=str(dbUser.longitude),
                    markers=markers
                    )  # get map, zoom on location of actual user, insert markers from select, ie users who provide specific required service

        return render_template("prehled_success.html", entries=vysledekselectu, sndmap=map)


@blueprint.route("/prehled_all", methods=["POST","GET"])
def prehled_all():

    services = DBAccess.ExecuteSQL("select * from services")
    checked_services_id_list = []
    for service in services:
        checked_services_id_list.append(service[0])

    form = regFormBuilder(
        services
    )  # put all services to form, but I need to display it - by for cycle below
    form.checkBoxes.clear()
    form.demandOffer.choices = [('2','poskytují pomoc'),('1','potřebují pomoc')]
 
    for index in form.checkBoxIndexes:
        checkbox = getattr(form, "checkbox%d" % index)
        if(request.method == 'GET'):
            checkbox.data = True
        form.checkBoxes.append(
            getattr(form, "checkbox%d" % index)
        )  # displaying checkboxes on website

    if form.validate_on_submit():
        checked_services_id_list = []
        for index in form.checkBoxIndexes:
            checkbox = getattr(form, "checkbox%d" % index)
            if checkbox.data:
                checked_services_id_list.append(checkbox.id)
        
    result = DBAccess.ExecuteSQL(
        '''
        SELECT u.id, u.first_name, u.surname, u.info, d.demand_offer, u.latitude, u.longitude, us.id,s.category
        FROM users u
        LEFT JOIN users_services us on us.id_users = u.id
        LEFT JOIN services s on s.id = us.id_services
        LEFT JOIN demand_offer d on d.id = us.id_demand_offer
        WHERE   d.id = %s AND
                us.id_services in %s
        ORDER BY u.id, us.id
        ''',(int(form.demandOffer.data),tuple(checked_services_id_list))
    )
    
    if result is None:
        result = []
        flash("Bohužel v systému nejsou zadány žádné služby  dle vašeho filtru.")


    usersCatDict = {}
    
    for row in result:
        key = list(row)
        key = tuple(key[:7])
        # key = tuple(list(row)[:7])
        value = row[-2:]
        if(key in usersCatDict):
            usersCatDict[key].append(value)
        else:
            usersCatDict[key] = [value]


    demandOfferText = 'nabízené'
    if(int(form.demandOffer.data)==1):
        demandOfferText = 'poptávané'
   
    dbUser = DBAccess.GetDBUserById(session['id_user'])

    # markery pro kazdeho vyhledaneho
    markers = []
    marker = {}
    marker["icon"] = "http://maps.google.com/mapfiles/kml/pal2/icon10.png"
    marker["lat"] = str(dbUser.latitude)
    marker["lng"] =  str(dbUser.longitude)
    marker["infobox"] = f'<b>{dbUser.first_name} </b><br>{dbUser.info}<img class=img_mapa src= {GetImageUrl(dbUser.id)} />'
    markers.append(marker)

    for user in usersCatDict.keys():
        servicesHTML = '<ul>'
        for service in usersCatDict[user]:
            servicesHTML=servicesHTML+f'<li> {service[1]} <a href="/match?id={service[0]}">Kontaktovat</a></li>'
        servicesHTML=servicesHTML+'</ul>'

        pictureUrl = GetImageUrl(user[0])
        marker = {}
        marker["icon"] = "http://maps.google.com/mapfiles/ms/icons/green-dot.png"
        marker["lat"] = str(user[5])
        marker["lng"] =  str(user[6])
        marker["infobox"] = f'''<b>{user[1]} {user[2]}</b><p>{user[3]}</p>\
            <img class=img_mapa src= {pictureUrl} /><br>\
            <p>{demandOfferText} služby: {servicesHTML}</p>'''
        markers.append(marker)

    map = Map(
                identifier="sndmap",
                style="height:100%;width:100%;margin:0;",
                lat=str(dbUser.latitude),
                lng=str(dbUser.longitude),
                markers=markers
                )  # get map, zoom on location of actual user, insert markers from select, ie users who provide specific required service

    return render_template("prehled_all.html", sndmap=map, form = form)
   
    
@blueprint.route("/podminky_seniori")
def podminky_seniori():
    return render_template("podminky_seniori.html")

@blueprint.route("/podminky_dobrovolnici")
def podminky_dobrovolnici():
    return render_template("podminky_dobrovolnici.html")

