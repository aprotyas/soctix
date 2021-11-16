from re import A
from flask_wtf import FlaskForm, form
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import (
    IntegerField,
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    RadioField,
    DateTimeField,
    BooleanField,
    SelectField,
)
from wtforms.fields.simple import EmailField

try:
    from wtforms.fields.html5 import DateField
except:
    from wtforms.fields import DateField
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Email,
    Length,
    EqualTo,
    ValidationError,
    NumberRange,
    Optional,
)
from ticketer.models import User


class Registration(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(-1, 20, "Username can be no longer than 20 characters"),
        ],
    )
    fname = StringField(
        "First name",
        validators=[Length(-1, 20, "First name can be no longer than 20 characters")],
    )
    lname = StringField(
        "Last name",
        validators=[Length(-1, 20, "Last name can be no longer than 20 characters")],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
            Length(-1, 20, "Email must be no longer than 20 characters"),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            Length(8, 20, "Password must be between 8 and 20 characters"),
            DataRequired(),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    street = StringField(
        "Street",
        validators=[Length(-1, 30, "Street can be no longer than 30 characters")],
    )
    city = StringField(
        "City", validators=[Length(-1, 20, "City can be no longer than 20 characters")]
    )
    state = StringField(
        "State", validators=[Length(2, 2, "State is a 2-character code")]
    )
    phone = StringField(
        "Phone",
        validators=[
            Length(min=10, max=10, message="Phone number must be 10 digits long")
        ],
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(Username=username.data).first()
        if user:
            raise ValidationError(
                "That username is taken. Please choose a different username."
            )

    def validate_email(self, email):
        user = User.query.filter_by(Email=email.data).first()
        if user:
            raise ValidationError(
                "That email is taken. Please choose a different email."
            )


class Login(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[Length(8, 20), DataRequired()])
    type = RadioField(
        "User Type",
        choices=[
            ("customer", "Customer"),
            ("employee", "Employee"),
            ("manager", "Team Manager"),
        ],
        validators=[DataRequired()],
    )
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign in")


class Lookup(FlaskForm):
    venue = StringField("Venue", validators=[Optional()])
    date = DateField("Date", format="%Y-%m-%d", validators=[Optional()])
    city = StringField("City", validators=[Optional()])
    team = StringField("Team Playing", validators=[Optional()])
    submit = SubmitField("Lookup")


class Update(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    picture = FileField(
        "Update Profile Picture", validators=[FileAllowed(["jpg", "png"])]
    )
    submit = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.Username:
            user = User.query.filter_by(Username=username.data).first()
            if user:
                raise ValidationError(
                    "That username is taken. Please choose a different username."
                )

    def validate_email(self, email):
        if email.data != current_user.Email:
            user = User.query.filter_by(Email=email.data).first()
            if user:
                raise ValidationError(
                    "That email is taken. Please choose a different email."
                )


class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):
        user = User.query.filter_by(Email=email.data).first()
        if not user:
            raise ValidationError("There is no account with this email!")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[Length(8, 20), DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset")


class AddEvent(FlaskForm):
    venue = StringField("Venue", validators=[DataRequired()])
    time = DateTimeField("Event Time", validators=[DataRequired()])
    opp_team = StringField("Opponent", validators=[DataRequired()])
    submit = SubmitField("Add")


class ChangeTicket(FlaskForm):
    ticket_id = IntegerField(
        "Ticket ID", validators=[DataRequired(), NumberRange(min=1)]
    )
    delete_ticket = BooleanField("Delete Ticket")
    new_price = IntegerField("New Price", validators=[NumberRange(min=1), Optional()])
    new_seat = IntegerField("New Seat ID", validators=[NumberRange(min=1), Optional()])
    submit = SubmitField("Modify")


class CheckoutForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    card_num = StringField("Card No.", validators=[DataRequired(), Length(15, 15)])
    exp_date = DateField("Expiration Date", validators=[DataRequired()])
    submit = SubmitField("Buy")
