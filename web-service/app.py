from flask import Flask, render_template, json, request
#from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash

#mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
#app.config['MYSQL_DATABASE_USER'] = 'jay'
#app.config['MYSQL_DATABASE_PASSWORD'] = 'jay'
#app.config['MYSQL_DATABASE_DB'] = 'BucketList'
#app.config['MYSQL_DATABASE_HOST'] = 'localhost'
#mysql.init_app(app)


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


if __name__ == "__main__":
    app.run(port=5002)
