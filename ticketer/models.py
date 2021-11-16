from flask import session
from flask_login.login_manager import LoginManager
from sqlalchemy.orm import backref
from ticketer import db, login_manager, app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class User(db.Model, UserMixin):
    __tablename__ = "Customer"
    ID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(40), unique=True, nullable=False)
    Email = db.Column(db.String(40), unique=True, nullable=False)
    Password = db.Column(db.String(20), nullable=False)
    FName = db.Column(db.String(40))
    LName = db.Column(db.String(40))
    Street = db.Column(db.String(40))
    City = db.Column(db.String(40))
    State = db.Column(db.String(2))
    Phone = db.Column(db.String(10))
    Performs = db.relationship("Transaction", backref=db.backref("Customer", lazy=True))

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id": self.ID})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id)

    def get_id(self):
        return self.ID


class Employee(db.Model, UserMixin):
    __tablename__ = "Employee"
    ID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(40), unique=True, nullable=False)
    Email = db.Column(db.String(40), unique=True, nullable=False)
    Password = db.Column(db.String(20), nullable=False)
    FName = db.Column(db.String(40))
    LName = db.Column(db.String(40))
    Phone = db.Column(db.String(10))
    Handles = db.relationship("Ticket", backref=db.backref("Employee", lazy=True))

    def get_id(self):
        return self.ID


class TeamManager(db.Model, UserMixin):
    __tablename__ = "TeamManager"
    ID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(40), unique=True, nullable=False)
    Email = db.Column(db.String(20), unique=True, nullable=False)
    Password = db.Column(db.String(20), nullable=False)
    FName = db.Column(db.String(40))
    LName = db.Column(db.String(40))
    Phone = db.Column(db.String(10))
    T_ID = db.Column(
        db.Integer,
        db.ForeignKey("Team.ID", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    Manages = db.relationship("Team", backref=db.backref("TeamManagers", lazy=True))

    def get_id(self):
        return self.ID


class Transaction(db.Model):
    __tablename__ = "Transaction"
    ID = db.Column(db.Integer, primary_key=True)
    Time = db.Column(db.DateTime, default=datetime.utcnow)
    C_ID = db.Column(
        db.Integer,
        db.ForeignKey("Customer.ID", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    Contains = db.relationship("Ticket", backref=db.backref("Transaction", lazy=True))


class Team(db.Model):
    __tablename__ = "Team"
    ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(20), nullable=False)
    PariticpatesInHome = db.relationship(
        "Event", back_populates="Team1", foreign_keys="Event.T1_ID"
    )
    ParticipatesInAway = db.relationship(
        "Event", back_populates="Team2", foreign_keys="Event.T2_ID"
    )


class Event(db.Model):
    __tablename__ = "Event"
    ID = db.Column(db.Integer, primary_key=True)
    Time = db.Column(db.DateTime, nullable=False)
    V_ID = db.Column(
        db.Integer,
        db.ForeignKey("Venue.ID", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    T1_ID = db.Column(
        db.Integer,
        db.ForeignKey("Team.ID", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    T2_ID = db.Column(
        db.Integer,
        db.ForeignKey("Team.ID", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    PlayedIn = db.relationship("Venue", backref=db.backref("Event", lazy=True))
    Team1 = db.relationship("Team", foreign_keys=[T1_ID])
    Team2 = db.relationship("Team", foreign_keys=[T2_ID])


class Ticket(db.Model):
    __tablename__ = "Ticket"
    ID = db.Column(db.Integer, primary_key=True)
    T_ID = db.Column(db.Integer, db.ForeignKey("Transaction.ID"))
    Em_ID = db.Column(
        db.Integer, db.ForeignKey("Employee.ID", ondelete="CASCADE", onupdate="CASCADE")
    )
    Ev_ID = db.Column(
        db.Integer, db.ForeignKey("Event.ID", ondelete="CASCADE", onupdate="CASCADE")
    )
    Price = db.Column(db.Float, db.CheckConstraint("Price>0.0"), nullable=False)
    Seat = db.Column(db.Integer, db.CheckConstraint("Seat>0"), nullable=False)
    Represents = db.relationship("Event", backref="Tickets", lazy=True)


class Venue(db.Model):
    __tablename__ = "Venue"
    ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(30), nullable=False)
    Capacity = db.Column(db.Integer, db.CheckConstraint("Capacity>0"))
    City = db.Column(db.String(20), nullable=False)
    State = db.Column(db.String(2), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    if session.get("account_type", "user") == "user":
        return User.query.get(int(user_id))
    elif session["account_type"] == "employee":
        return Employee.query.get(int(user_id))
    elif session["account_type"] == "manager":
        return TeamManager.query.get(int(user_id))
