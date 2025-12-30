from flask import Flask, render_template, session, request, url_for, redirect, jsonify
from flask_wtf import CSRFProtect
from typing import List, Optional
from sqlmodel import Field, SQLModel, Column, JSON, create_engine, Session
from flask_apscheduler import APScheduler
from email_validator import validate_email, EmailNotValidError
from flask_session import Session as FlaskSession
from dotenv import load_dotenv
from flask_mailman import Mail, EmailMultiAlternatives
from datetime import datetime
from redis import Redis
import requests
import string
import secrets
import random
import os
import json
import time

load_dotenv('.env')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS')
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
app.config['MAIL_RECIPIENT'] = os.environ.get('MAIL_RECIPIENT')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['DICTIONARY_API'] = os.environ.get('DICTIONARY_API')
app.config['REDIS_URL'] = os.environ.get('REDIS_URL')
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'wordsmith_session:'
app.config['SESSION_REDIS'] = os.environ.get('REDIS_URL')
scheduler = APScheduler()
csrf = CSRFProtect(app)
mail = Mail(app)
db_engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
redis = Redis.from_url(app.config['REDIS_URL'], decode_responses=True)
FlaskSession(app)


class EmailSender:
    def send_email():
        pass

class Passcode:
    def generate_passcode():
        return ''.join(secrets.choice(string.digits) for i in range(8))

    def store_passcode(email):
        passcode_key = secrets.token_urlsafe(16) 
        passcode = Passcode.generate_passcode()
        redis.setex(
            f'passcode:{passcode_key}',
            6000,
            json.dumps({'email' : email, 'passcode' : passcode, 'attempts' : 0})
        )
        return passcode_key, passcode
    
    def send_passcode(email):
        try:
            wotd = EmailMultiAlternatives(
                subject='Passcode', 
                body=render_template('email.txt', passcode=Passcode.generate_passcode()),
                from_email=app.config['MAIL_USERNAME'], 
                to=[email]
            )
            wotd.attach_alternative(render_template('email.html', passcode=Passcode.generate_passcode()), 'text/html')
            wotd.send()
        except Exception as e:
            return f'error: {str(e)}'

    def verify_passcode(passcode_key, passcode):
        if data := redis.get(f'passcode:{passcode_key}'):
            passcode_data = json.loads(data)
            if passcode_data['attempts'] >= 3 ot passcode_data['passcode'] != passcode:
                return None
        else:
            return None
    

class User(SQLModel, table=True):
    __tablename__ = 'users'
    user_id: Optional[int] = Field(default=None, primary_key=True)
    fullname: str = Field(default='anonymous')
    email: str  = Field(unique=True)
    date_created : datetime = Field(default=datetime.now())
    last_active: datetime = Field(default=datetime.now())

    def get_subscribers():
        pass

    def save_user(self, db_engine):
        try:
            with Session(db_engine) as session:
                session.add(self)
                session.commit()
                session.close()
                return 'User saved', 200 
        except Exception as e:
            return f'Unable to save user: {e}', 400


class Wordbank(SQLModel, table=True):
    word_id: int = Field(default=None, primary_key=True)
    word: str
    phonetic: str
    meanings: List[str] = Field(sa_column=Column(JSON))
    audio: str = Field(default=None)
    user_id: int
    date_added: datetime

    def get_word(word):
        return requests.get(f"{app.config['DICTIONARY_API']}/{word}")   

    def new_word():
        '''Return a word that has not been sent to the user'''
        pass

    def check_words(word):
        '''Check db for word and if it doesnt exist in db return it. 
           Otherwise, run random_word() again 
        '''
        pass

    def save_word(word):
        '''Save word to db'''
        pass

    def random_word():
        words = []
        with open('words.txt', 'r') as file:
            for line in file:
                words.append(line.rstrip())
        random_word = random.choice(words)
        word = Wordbank.get_word(random_word)
        return word.json()
    
    def get_synonyms(word):
        word_definition = Wordbank.get_word(word)
        word_data = word_definition.json()
        for result in word_data:
                for item in result['meanings']:
                    for word in item['definitions']:
                        if len(word['synonyms']) == 0:
                            return 'Unable to find the word provided'
                        else:
                            return word['synonyms']
    def send_word():
        with app.app_context():
            emails = User.get_subscribers()
            word = Wordbank.new_word()
            for email in emails:
                try:
                    wotd = EmailMultiAlternatives(
                        subject='Word of The Day', 
                        body=render_template('wotd.txt', wotd=word),
                        from_email=app.config['MAIL_USERNAME'], 
                        to=[email]
                    )
                    wotd.attach_alternative(render_template('wotd.html', wotd=word), 'text/html')
                    wotd.send()
                    print('e-mail sent')
                except Exception as e:
                    return f'error: {str(e)}'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User(email=email)
        user.save_user(db_engine)
    return render_template('index.html', title='Get a Word a Day')

@app.route('/register', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        user = User(fullname=name, email=email)
        user.save_user(db_engine)
        user_passcode = Passcode.send_passcode(email)

        return redirect(url_for('registration_passcode'))
    return render_template('register.html', title='Registration')

@app.route('/register/passcode', methods=['POST'])
def registration_passcode():        
    return render_template('passcode.html', title='Passcode')

@app.route('/signin')
def signin():
    return render_template('signin.html', title='Sign in')

@app.route('/signin/passcode')
def signin_passcode():
    return render_template('passcode.html', title='Passcode')

@app.route('/email/passcode')
def send_passcode():
    send = Passcode.send_passcode()
    return {'success' : 200}

@app.route('/email/wotd')
def send_wotd():
    pass

@app.route('/wordbank')
def wordbank():
    pass

@app.route('/wordbank/delete/<word_id>')
def delete_word():
    pass

@app.route('/wordbank/<word_id>')
def get_word():
    pass

@app.route('/wordbank/bookmark/<word_id>')
def bookmark_word():
    pass

@app.route('/signout')
def signout():
    return render_template('signout.html')
    
@app.route('/api/documentation')
def docs():
    return render_template('documentation.html', title='Documentation')

@app.route('/api/search/<word>')
def word_search(word):
    dictionary_result = Wordbank.get_word(word)
    return dictionary_result.json()

@app.route('/api/random/word')
def randomize():
    random_word = Wordbank.random_word()
    if isinstance(random_word, dict):
        time.sleep(0.5)
        return redirect(url_for('randomize'))
    else:
        return random_word

@app.route('/api/synonyms/<word>')
def synonyms(word):
    synonym = Wordbank.get_synonyms(word)
    return synonym

if __name__ == '__main__':
    scheduler.add_job(
        id='wotd-job', 
        func=Wordbank.send_word, 
        trigger='cron', 
        day_of_week='*', 
        hour=10, 
        minute=30, 
        misfire_grace_time=3600
    )
    scheduler.start()
    app.run(debug=True, use_reloader=False)