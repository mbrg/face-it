from flask import Flask, render_template, json, request, url_for, redirect, send_from_directory
#from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from os.path import join, exists


# globals
UPLOAD_FOLDER = '/home/dsteam/repos/face-it/web-service/tmp/'
GIFS_FOLDER = '/home/dsteam/repos/face-it/web-service/gifs/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
FILE_CNTR = 0

#mysql = MySQL()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploads', methods=['GET', 'POST'])
def upload_file():
    """
    ref: http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
    """
    global FILE_CNTR

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # save file
            cnt_filename = '%d.jpg' % FILE_CNTR
            file.save(join(app.config['UPLOAD_FOLDER'], cnt_filename))

            red = redirect(url_for('uploaded_file', filename='%d.gif' % FILE_CNTR))  # redirects to /uploads/filename

            FILE_CNTR += 1
            return red
    return render_template('upload.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):

    filepath = join(GIFS_FOLDER, filename)

    if exists(filepath) :
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else:
        return render_template('not_ready.html')


if __name__ == "__main__":
    app.run(port=5002)
