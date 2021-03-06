from flask import Flask, render_template
from back import User

app = Flask(__name__, template_folder='website')
# app.run(port='8888')

'''
to start flask server
set FLASK_APP=front.py
set FLASK_DEBUG=1
flask run
'''
cur_user = User('ef2607b740534db4a708db8b6feb6e2f', '410147f8a9be40fc8630a12ae1ccf0b3', 'titooooo27',
                scope='user-read-recently-played')


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', page='User Data', current_song=cur_user.current_song())


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(port='8888')  # testing this out. if this causes an issue uncomment above app.run(...) and delete this
    app.run(debug=True)
