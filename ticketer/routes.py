import secrets

import random
from datetime import datetime
from flask import render_template, url_for, flash, redirect, request, abort, session
from ticketer.forms import (
    Registration,
    Login,
    Update,
    Lookup,
    RequestResetForm,
    ResetPasswordForm,
    AddEvent,
    ChangeTicket,
    CheckoutForm,
)
from ticketer import app, db, mail
from ticketer.models import (
    User,
    Employee,
    TeamManager,
    Transaction,
    Team,
    Event,
    Ticket,
    Venue,
)
from flask_login import login_required, login_user, current_user, logout_user
from flask_mail import Message
from sqlalchemy import and_, func


@app.context_processor
def inject_user():
    events = Event.query.all()
    random.shuffle(events)
    show_events = events[:5]
    map = {}
    count = 1

    for event in show_events:
        map[
            "event" + str(count)
        ] = f'{event.Team1.Name} vs {event.Team2.Name} {event.Time.strftime("%m/%d/%Y | %H:%M")}'
        count += 1
    return map


@app.route("/", methods=["POST", "GET"])
def home():
    account_type = session.get("account_type", "user")
    if account_type == "employee":
        return employee_home()
    elif account_type == "manager":
        return manager_home()
    form = Lookup()
    if form.validate_on_submit():
        # collects all query params
        # uses only those params that have been used
        venue = form.venue.data
        date = form.date.data
        team = form.team.data
        query = Event.query
        if venue:
            venue_id = Venue.query.filter_by(Name=venue).first().ID
            query = query.filter_by(V_ID=venue_id)
        if date:
            query = query.filter(func.date(Event.Time) == date)
        if team:
            team_id = Team.query.filter_by(Name=team).first().ID
            query = query.filter((Event.T1_ID == team_id) | (Event.T2_ID == team_id))
        return search_results(query)
    return render_template("lookup.html", form=form)


@app.route("/search_results", methods=["GET", "POST"])
def search_results(query):
    page = request.args.get("page", 1, type=int)
    events = query.order_by(Event.Time.desc()).paginate(page=page, per_page=5)
    return render_template("events.html", events=events)


def create_tickets(event):
    num_tix = 20
    while num_tix > 0:
        price = random.randint(40, 100)
        seatnum = random.randint(1, 1000)
        if seatnum in [t.Seat for t in Ticket.query.all()]:
            continue
        emp_id = random.randint(1, len(Employee.query.all()))
        print(f"Event ID: {event.ID}")
        ticket = Ticket(Em_ID=emp_id, Ev_ID=event.ID, Price=price, Seat=seatnum)
        db.session.add(ticket)
        db.session.commit()
        num_tix -= 1


@app.route("/manager/home", methods=["POST", "GET"])
@login_required
def manager_home():
    form = AddEvent()
    if form.validate_on_submit():
        try:
            venue_id = Venue.query.filter_by(Name=form.venue.data).first().ID
        except:
            venue = Venue(Name=form.venue.data, Capacity=500, City="None", State="AL")
            db.session.add(venue)
            db.session.commit()
            venue_id = venue.ID
        op_team_id = Team.query.filter_by(Name=form.opp_team.data).first().ID
        time = form.time.data
        new_event = Event(
            Time=time, V_ID=venue_id, T1_ID=current_user.T_ID, T2_ID=op_team_id
        )
        db.session.add(new_event)
        db.session.commit()
        create_tickets(new_event)
        flash("Event Added!", "success")
        return redirect(url_for("events"))
    return render_template("manager_home.html", form=form)


@app.route("/employee/home", methods=["POST", "GET"])
@login_required
def employee_home():
    form = ChangeTicket()
    if form.validate_on_submit():
        ticket_id = form.ticket_id.data
        new_price = form.new_price.data
        new_seat = form.new_seat.data
        delete_ticket = form.delete_ticket.data
        ticket = Ticket.query.filter_by(ID=ticket_id, Em_ID=current_user.ID).first()
        if ticket:
            if delete_ticket:
                # delete ticket
                db.session.delete(ticket)
            elif new_price or new_seat:
                # update ticket
                if not new_price:
                    new_price = ticket.Price
                if not new_seat:
                    new_seat = ticket.Seat
                ticket.Price = new_price
                ticket.Seat = new_seat
            db.session.commit()
            flash("Ticket Modified!", "success")
        else:
            flash("Ticket does not exist!", "warning")
    page = request.args.get("page", 1, type=int)
    tickets = Ticket.query.filter_by(Em_ID=current_user.ID).paginate(
        page=page, per_page=3
    )
    return render_template("employee_home.html", form=form, tickets=tickets)


@app.route("/events")
def events():
    page = request.args.get("page", 1, type=int)
    events = Event.query.order_by(Event.Time.desc()).paginate(page=page, per_page=5)
    return render_template("events.html", events=events)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = Registration()
    if form.validate_on_submit():
        user = User(
            Username=form.username.data,
            Email=form.email.data,
            Password=form.password.data,
            FName=form.fname.data,
            LName=form.lname.data,
            Street=form.street.data,
            City=form.city.data,
            State=form.state.data,
            Phone=form.phone.data,
        )
        db.session.add(user)
        db.session.commit()
        flash(
            f"Account created for {form.username.data}! You are now able to log in.",
            "success",
        )
        return redirect(url_for("login"))
    return render_template("register.html", form=form, title="Register")


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = Login()
    if form.validate_on_submit():
        type_map = {
            "customer": (User, "home"),
            "employee": (Employee, "employee"),
            "manager": (TeamManager, "manager"),
        }
        print(form.type.data)
        UserTypeTup = type_map[form.type.data]
        UserType = UserTypeTup[0]
        if form.type.data == "customer":
            session["account_type"] = "user"
            redirect_url = UserTypeTup[1]
        else:
            session["account_type"] = UserTypeTup[1]
            redirect_url = UserTypeTup[1] + "_home"
        user = UserType.query.filter_by(Email=form.email.data).first()
        if user and user.Password == form.password.data:
            login_user(user, remember=form.remember_me.data)
            if isinstance(user, User):
                next_page = request.args.get(
                    "next"
                )  # to redirect to the page the user wanted to access before being asked to login
                return (
                    redirect(next_page)
                    if next_page
                    else redirect(url_for(redirect_url))
                )
            else:
                return redirect(url_for("home"))

            ##### FIX THIS FOR NOT CUSTOMERS
        else:
            flash(f"Login Unsuccessful! Check username and password", "danger")
    return render_template("login.html", form=form, title="Login")


@app.route("/logout")
def logout():
    try:
        session.pop("account_type")
    except:
        pass
    logout_user()
    return redirect(url_for("home"))


#### PASS IN EV_ID???
@app.route("/<int:event_id>/checkout", methods=["GET", "POST"])
@login_required
def checkout(event_id):
    form = CheckoutForm()
    if form.validate_on_submit():
        expdate = form.exp_date.data
        # get user ID: current_user.ID
        user_ID = current_user.ID
        # if expdate is before today, don't go
        if datetime.now().date() > expdate:
            flash("Check the expiration date of your card!", "warning")
        else:
            tickets = Ticket.query.filter_by(Ev_ID=event_id, T_ID=None).all()
            if tickets:
                ticket = random.choice(tickets)
                transaction = Transaction(C_ID=user_ID)
                db.session.add(transaction)
                db.session.commit()
                ticket.T_ID = transaction.ID
                db.session.commit()
                send_ticket_email(current_user, ticket)
                flash("Ticket purchased!", "success")
                return redirect(url_for("home"))
            else:
                flash("No tickets exist for this event", "danger")
        # set transaction ID in the ticket
        # randomly give one of the tickets to the customer
        # event = Event.query.get_or_404(event_id)
        # find all tickets with given event ID
    return render_template("checkout.html", form=form)


def send_ticket_email(user, ticket):
    msg = Message(
        "Ticket Purchased", sender="noreply@demo.com", recipients=[user.Email]
    )
    name = f"{user.FName} {user.LName}"
    event = ticket.Represents
    msg.body = f"""
Hello, {name}\n
---------------------------------------
Here is your ticket info for the event:
{event.Team1.Name} vs {event.Team2.Name} at {event.PlayedIn.Name}
Seat - {ticket.Seat}
Time - {event.Time}
Thank you for buying your ticket with us.
        """
    mail.send(msg)


@app.route("/account", methods=["POST", "GET"])
@login_required
def account():
    form = Update()
    if form.validate_on_submit():
        current_user.Username = form.username.data
        current_user.Email = form.email.data
        db.session.commit()
        flash("Account updated!", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.Username
        form.email.data = current_user.Email
    return render_template("account.html", title="Account", form=form)


def send_reset_email(user: User):
    token = user.get_reset_token()
    msg = Message(
        "Password Reset Request", sender="noreply@demo.com", recipients=[user.Email]
    )
    msg.body = f"""
To reset your password, visit the following link:
{url_for('reset_password', token=token, _external=True)}

If you did not make this request, then ignore this email and no changes will be made.
    """
    mail.send(msg)


@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(Email=form.email.data).first()
        send_reset_email(user)
        flash("Email has been sent with instructions to reset password.", "info")
        return redirect(url_for("login"))
    return render_template("reset_request.html", title="Reset Password", form=form)


@app.route("/reset_password/<string:token>", methods=["GET", "POST"])
def reset_password(token: str):
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    user = User.verify_reset_token(token)
    if not user:
        flash("That is an invalid or expired token!", "warning")
        return redirect(url_for("reset_request"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.Password = form.password.data
        db.session.commit()
        flash("Your password has been updated. You can now login!", "success")
        return redirect(url_for("login"))
    return render_template("reset_password.html", title="Reset Password", form=form)


@app.route("/about")
def about():
    return render_template("about.html", title="About")
