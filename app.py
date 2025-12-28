from flask import Flask, render_template, session, request, url_for, redirect, jsonify
from flask_wtf import CSRFProtect
from typing import List
from sqlmodel import Field, SQLModel, Column, JSON, create_engine
from dotenv import load_dotenv
from flask_mail import Mail, Message
from datetime import datetime
from redis import Redis
import requests
import random
import os
import sys
import json
import time

load_dotenv('.env')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['DICTIONARY_API'] = os.environ.get('DICTIONARY_API')
app.config['REDIS_URL'] = os.environ.get('REDIS_URL')
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

    def get_word(word):
        return requests.get(f"{app.config['DICTIONARY_API']}/{word}")   

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
    return render_template('signout.html')
    
@app.route('/api/documentation')
def docs():
    return render_template('documentation.html', title='Documentation')

@app.route('/api/words/<letter>')
def letter():
    pass

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
    app.run(debug=True)