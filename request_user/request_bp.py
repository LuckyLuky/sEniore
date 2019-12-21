from flask import (
    Blueprint,
    request,
    render_template,
    abort,
    )
from dbaccess import DBAccess,DBUser
from utils import LoginRequired, flash, FlashStyle
from lookup import RequestStatus


blueprint = Blueprint("request_bp", __name__, template_folder="templates")


@blueprint.route("/requests", methods=["GET", "POST"])
@LoginRequired(2)
def requests():
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
        inner join requests_status rs on r.id_requests_status = rs.id"""
    )
    return render_template("requests.html", entries=requests)


@blueprint.route("/requests_detail", methods=["GET", "POST"])
@LoginRequired()
def requests_detail():
    rid = request.args.get("id", type=int)

    if request.method == "POST":
        # status = request.form["submit_button"]
        status = RequestStatus[request.form["submit_button"]]
        DBAccess.ExecuteUpdate(
            "UPDATE requests SET id_requests_status= %s where id= %s", (status, rid)
        )
    
    requests = DBAccess.ExecuteSQL(
        """select
          ud.first_name,
          ud.surname,
          ud.email,
          ud.telephone,
          ud.town,
          uo.first_name,
          uo.surname,
          uo.email,
          uo.telephone,
          uo.town,
          s.category,
          r.date_time,
          r.add_information,
          to_char(r.timestamp, 'YYYY-mm-DD HH12:MI:SS'),
          rs.status,
          r.id,
          ud.id,
          uo.id
        from requests r
        inner join services s on r.id_services = s.id
        inner join users ud on r.id_users_demand = ud.id
        inner join users uo on r.id_users_offer = uo.id
        inner join requests_status rs on r.id_requests_status = rs.id
        where r.id =%s""",
        (rid,))
        
    if(requests is None):
         abort(403)
    requests = requests[0]
    dbUser = DBUser.LoadFromSession('dbUser')
    if dbUser.level<2 and dbUser.id != int(requests[16]) and dbUser.id != int(requests[17]):
        abort(403)
        

    
    return render_template("requests_detail.html", entries=requests)
