from flask import Flask, render_template, session
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
import os

load_dotenv('.env')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
csrf = CSRFProtect(app)



@app.route('/')
def index():
    return render_template('index.html', title='Get a Word a Day')

@app.route('/register')
def registration():
    pass

@app.route('/register/passcode')
def registration_passcode():
    pass

@app.route('/signin')
def signin():
    pass

@app.route('/signin/passcode')
def signin_passcode():
    pass

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
    pass

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