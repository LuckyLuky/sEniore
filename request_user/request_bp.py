from flask import (
    Blueprint,
    request,
    render_template,
    abort,
    url_for,
    redirect
    )
from dbaccess import DBAccess, DBUser
from utils import LoginRequired, flash, FlashStyle, SendMail
from lookup import RequestStatus, RequestStatusUser
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    SubmitField,
)
from wtforms.validators import InputRequired, DataRequired, Length, number_range
from wtforms.widgets import TextArea

blueprint = Blueprint("request_bp", __name__, template_folder="templates")

class FeedbackFormular(FlaskForm):
    comment = StringField("Napište krátké ohodnocení:", widget=TextArea(), validators=[DataRequired()])
    number_evaluation = IntegerField( validators=[InputRequired(), number_range(1, 5)], )
    submit = SubmitField(
      "Odeslat hodnocení", render_kw=dict(class_="btn btn-outline-primary btn-block")
    )



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
    if(requests == None):
      requests = []
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
          to_char(r.timestamp, 'YYYY-mm-DD HH12:MI'),
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


@blueprint.route("/feedback", methods=["GET", "POST"])
@LoginRequired()
def feedback():
  range_evaluation = range(1,6)
  form = FeedbackFormular()
  rid = request.args.get("id", type=int)
  dbUser = DBUser.LoadFromSession('dbUser')
  id_user_review = dbUser.id
  
  id_users = DBAccess.ExecuteSQL(
        """select
        id_users_demand, id_users_offer
        from requests 
        where id =%s""",
        (rid,))

  if id_users[0][0]== id_user_review:
    id_user_evaluated = id_users[0][1]
  else:
    id_user_evaluated = id_users[0][0]
  
  if form.validate_on_submit():
    comment = form.comment.data
    number_evaluation = request.form["number_evaluation"]
    DBAccess.ExecuteInsert(
      """insert into feedback
         (id_requests, id_user, id_user_review, comment, evaluation)
         values (%s, %s, %s, %s, %s)""",
         (rid, id_user_evaluated, id_user_review, comment, number_evaluation))
    DBAccess.ExecuteUpdate(
      """update requests
      set id_requests_status = 5 
      where id =%s""",
        (rid,))
  
    return render_template("feedback_thanks.html")

  return render_template("feedback.html", form = form, range_evaluation = range_evaluation)

@blueprint.route("/requests_detail_user", methods=["GET", "POST"])
@LoginRequired()
def requests_detail_user():
    rid = request.args.get("id", type=int)
    dbUser = DBUser.LoadFromSession('dbUser')
    userId = dbUser.id
         
    requests = DBAccess.ExecuteSQL(
        """select s.category, 
            
            case when 	ud.id = %s
            then	uo.first_name 
            else	ud.first_name
            end,
            
            case when 	ud.id = %s
            then	uo.surname 
            else	ud.surname
            end,
			
		      	case when 	ud.id = %s
            then	uo.email 
            else	ud.email
            end,
          
          r.date_time,
          r.id,
          ud.id,
          uo.id,
          r.id_users_creator
        from requests r
        inner join services s on r.id_services = s.id
        inner join users ud on r.id_users_demand = ud.id
        inner join users uo on r.id_users_offer = uo.id
        inner join requests_status rs on r.id_requests_status = rs.id
        where r.id =%s""",
        (userId, userId, userId, rid))
            
    if(requests is None):
         abort(403)
    requests = requests[0]
    dbUser = DBUser.LoadFromSession('dbUser')
    if dbUser.level<2 and dbUser.id != int(requests[6]) and dbUser.id != int(requests[7]):
        abort(403)

    acceptButtonVisible = (int(requests[8])!=userId)
        
    if request.method == "POST":
          # status = request.form["submit_button"]
          status = RequestStatusUser[request.form["submit_button"]]
          DBAccess.ExecuteUpdate(
              "UPDATE requests SET id_requests_status= %s where id= %s", (status, rid)
          )
          text = 'potvrzena' if status == '2' else 'zamítnuta'
          SendMail('noreply@seniore.org', requests[3], 'Seniore.org - změna stavu vaší žádosti', 
          f'Vaše žádost / nabídka na činnost {requests[0]} dne {requests[4]} byla {text}.')
          return redirect(url_for("profile_bp.user_request_overview")) 

    return render_template("request_detail_user.html", entries=requests, acceptButtonVisible = acceptButtonVisible)