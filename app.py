from flask import Flask, render_template, session
from flask_wtf import CSRFProtect
from typing import List
from sqlmodel import Field, SQLModel, Column, JSON, create_engine
from dotenv import load_dotenv
from flask_mail import Mail, Message
from datetime import datetime
import os

load_dotenv('.env')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
csrf = CSRFProtect(app)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    fullname: str
    email: str 
    date_created : datetime
    last_active: datetime

class Wordbank(SQLModel, table=True):
    word_id: int = Field(default=None, primary_key=True)
    word: str
    phonetic: str
    meanings: List[str] = Field(sa_column=Column(JSON))
    audio: str = Field(default=None)
    user_id: int
    date_added: datetime


@app.route('/')
def index():
    return render_template('index.html', title='Get a Word a Day')

@app.route('/register')
def registration():
    return render_template('register.html', title='Registration')

@app.route('/register/passcode')
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
    pass
    
@app.route('/api/documentation')
def docs():
    return render_template('documentation.html', title='Documentation')

@app.route('/api/words/<letter>')
def letter():
    pass

@app.route('/api/search/<word>')
def word_search():
    pass

@app.route('/api/random/word')
def random_word():
    pass

@app.route('/api/synonyms/<word>')
def synonyms():
    pass


if __name__ == '__main__':
    app.run(debug=True)