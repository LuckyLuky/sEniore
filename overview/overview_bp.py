from flask import (
    Blueprint,
    request,
    render_template,
   )
from flask_wtf import FlaskForm
from wtforms import RadioField
from dbaccess import DBAccess

blueprint = Blueprint("overview_bp", __name__, template_folder="templates")


class OverviewFormBase(FlaskForm):
    demandOffer = RadioField(
        "Nabídka/Poptávka", choices=[("2", "nabídka"), ("1", "poptávka")], default="2"
    )


@blueprint.route("/prehled", methods=["POST", "GET"])
def prehled_filtr():
    form = OverviewFormBase()
    services = DBAccess.ExecuteSQL("select * from services")
    addresses = DBAccess.ExecuteSQL("select distinct town from users")
    if request.method == "GET":
        return render_template(
            "prehled.html", form=form, services=services, addresses=addresses
        )

    elif request.method == "POST":
        vysledekselectu = DBAccess.ExecuteSQL(
            """
        SELECT u.first_name, u.surname, s.category, d.demand_offer, u.town, us.id
        FROM users u
        LEFT JOIN users_services us on us.id_users = u.id
        LEFT JOIN services s on s.id = us.id_services
        LEFT JOIN demand_offer d on d.id = us.id_demand_offer
        WHERE d.id = %s and s.id = %s and lower(u.town) = lower(%s)
        ORDER BY us.id desc
        LIMIT 10
        """,
            (form.demandOffer.data, request.form["category"], request.form["address"])
        )
        if vysledekselectu is None:
            vysledekselectu = []
        return render_template("prehled_success.html", entries=vysledekselectu)
