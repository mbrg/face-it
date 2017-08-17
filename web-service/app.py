from flask import Flask, render_template, json, request
#from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
import datetime, os, sqlite3, time

#mysql = MySQL()
app = Flask(__name__)
db_path = '//database.db'
_secret = 'secret_cookie_recipe'

# MySQL configurations
#app.config['MYSQL_DATABASE_USER'] = 'jay'
#app.config['MYSQL_DATABASE_PASSWORD'] = 'jay'
#app.config['MYSQL_DATABASE_DB'] = 'BucketList'
#app.config['MYSQL_DATABASE_HOST'] = 'localhost'
#mysql.init_app(app)


def insertUser(user_id,name,picture, score = 0):
    con = sql.connect("database.db")
    cur = con.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, name,profile_picture,score) VALUES (?,?,?,?)", (user_id, name,profile_picture,score))
    con.commit()
    con.close()

@app.route('/')
def main():
    return render_template('index2.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


if __name__ == "__main__":
    app.run(port=5002)




















"""
import bottle, datetime, os, sqlite3, time

app     = bottle.Bottle()
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
_secret = 'secret_cookie_recipe'

bottle.TEMPLATE_PATH.append(os.path.join(os.path.dirname(__file__), 'views'))

def create_db():
    with sqlite3.connect(db_path) as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                user_id  INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT
            );
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY,
                user_id    INTEGER REFERENCES users (user_id),
                timestamp  INTEGER,
                message    TEXT
            );
            INSERT OR IGNORE INTO users VALUES (1, 'alice', 'ComplicatedP4ssw0rd!');
            INSERT OR IGNORE INTO users VALUES (2, 'bob', '@c0mpl1catedPASSWORD');
            INSERT OR IGNORE INTO users VALUES (3, 'mallory', '1234');
            INSERT OR IGNORE INTO messages VALUES (1, 1, 1420106400, 'Hey, Bob!');
            INSERT OR IGNORE INTO messages VALUES (2, 2, 1420106415, 'Hi Alice!');
        ''')

def login_required(function):
    def decorated(*args, **kwds):
        create_db()
        cookie = bottle.request.get_cookie('user', secret=_secret)
        if not cookie or ':' not in cookie:
            return bottle.template('login')
        username, password = cookie.split(':', 1)
        with sqlite3.connect(db_path) as conn:
            if not conn.execute("SELECT * FROM users WHERE username = '%s' AND password = '%s'" % (username, password)).fetchall():
                return bottle.template('login')
        return function(username, *args, **kwds)
    return decorated

@app.post('/login')
def login():
    bottle.response.set_cookie('user', '%s:%s' % (bottle.request.POST.get('username'), bottle.request.POST.get('password')), secret=_secret)
    return bottle.redirect('/')

@app.get('/logout')
def logout():
    bottle.response.delete_cookie('user')
    return bottle.redirect('/')

@app.get('/')
@login_required
def index(username):
    with sqlite3.connect(db_path) as conn:
        posts = [{
            'username'  : username_,
            'timestamp' : datetime.datetime.fromtimestamp(int(timestamp)).strftime('%d.%m.%Y %H:%M:%S'),
            'message'   : message,
        } for username_, timestamp, message in conn.execute('SELECT username, timestamp, message FROM users NATURAL JOIN messages').fetchall()]
    return bottle.template('index', username=username, posts=posts)

@app.post('/post')
@login_required
def post(username):
    message = bottle.request.POST['message']
    with sqlite3.connect(db_path) as conn:
        user_id, = conn.execute("SELECT user_id FROM users WHERE username = '%s'" % username).fetchone()
        conn.execute('INSERT INTO messages (user_id, timestamp, message) VALUES (?, ?, ?)', (user_id, int(time.time()), message))
    return bottle.redirect('/')

@app.get('/reset')
def reset():
    if os.path.exists(db_path):
        os.remove(db_path)
    return bottle.redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
"""
