from flask import Flask, render_template, json, request
# from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
import datetime, os, sqlite3, time

# mysql = MySQL()
app = Flask(__name__)
db_path = 'database.db'
_secret = 'secret_cookie_recipe'


# MySQL configurations
# app.config['MYSQL_DATABASE_USER'] = 'jay'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'jay'
# app.config['MYSQL_DATABASE_DB'] = 'BucketList'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# mysql.init_app(app)


def create_db():
    with sqlite3.connect(db_path) as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                user_id  INTEGER PRIMARY KEY,
                name TEXT,
                profile_picture TEXT,
                score INTEGER
            );

            INSERT OR IGNORE INTO users VALUES (10155120752592261,'Guy Yom Tov', 'https://fb-s-b-a.akamaihd.net/h-ak-fbx/v/t31.0-1/p720x720/1965679_10151936638602261_1862136309_o.jpg?oh=0a7f64fe64dfcfa88eb951c369a50376&oe=5A2A545A&__gda__=1511622788_b9288a930f60600db1674768a23203d5', 0);
        ''')

create_db()