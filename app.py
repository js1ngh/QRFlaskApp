import os
import base64
from io import StringIO
from flask import Flask, render_template, redirect, url_for, flash, session, \
    abort, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user, \
    current_user
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Required, Length, EqualTo
from twilio.rest import Client # FOR SMS
from random import randint
import onetimepass
import pyqrcode

# create application instance
app = Flask(__name__)
app.config.from_object('config')

# initialize extensions
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
lm = LoginManager(app)

class Event(UserMixin, db.Model):
    """Event model."""
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    eventname = db.Column(db.String(64), index=True)
    externalID = db.Column(db.String(64))

    def __init__(self, **kwargs):
        super(Event, self).__init__(**kwargs)


class EventForm(Form):
    """Registration Form for an event"""
    eventname = StringField('Name of Event', validators=[Required()])
    externalID = StringField('Event ID', validators=[Required()])
    submit = SubmitField('Register Event')

class LoginForm(Form):
    """Login form."""
    token = StringField('Token', validators=[Required()])
    submit = SubmitField('Login')
    
@app.route('/', methods=['GET'])
def index():
    if request.args.get('name') == "" or request.args.get('name') == None or request.args.get('phone') == "" or request.args.get('phone') == None:
        return render_template('index.html')
    else:
        name = request.args.get('name')
        phone = request.args.get('phone')
        eventid = request.args.get('id')
        token = randint(1000, 9999)
        session['name'] = name
        session['phone'] = phone
        session['token'] = token
        return redirect(url_for('two_factor_setup'))

@app.route('/eventregisteration', methods=['GET', 'POST'])
def eventregisteration():
    form = EventForm()
    if form.validate_on_submit():
        #        e_id = Event.query.filter_by(eventname=form.eventname.data).first()
        #if e_id is not None:
        #    flash('Event already exists.')
        #    return redirect(url_for('eventregisteration'))
        new_event = Event(eventname=form.eventname.data,
                          externalID=form.externalID.data)
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('event.html', form=form)

@app.route('/two-factor-setup')
def two_factor_setup():
    return render_template('two-factor-setup.html'), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}

@app.route('/qrcode')
def qrcode():
    url = pyqrcode.create(url_for('login', _external=True))
    stream = StringIO()
    url.svg(stream, scale=9)
    return stream.getvalue().encode('utf-8'), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    twilio_number = '16463625451'
    to_number = session['phone']
    sms_info = session['token']
    account_sid = 'AC7451e99f2a0cd5dff7233b17bb59203a'
    auth_token = 'dda90d9e299910ce9159cc9e08f715a3'
    client = Client(account_sid, auth_token)
    client.api.messages.create(to_number, from_=twilio_number, body=sms_info)
    if form.validate_on_submit():
        if int(form.token.data) != (sms_info):
            flash('Invalid username, password or token.')
            return redirect(url_for('index'))
        flash('Success')
        return redirect(url_for('ticket'))
    return render_template('login.html', form=form)

@app.route('/ticket', methods=['GET', 'POST'])
def ticket():
    return render_template('ticket.html')

# create database
db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
