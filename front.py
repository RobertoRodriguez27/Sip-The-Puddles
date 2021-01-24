from flask import Flask, render_template
# from back import User

app = Flask(__name__)
# app.run(port='8888')

'''
to start flask server
set FLASK_APP=front.py
flask run
'''


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', page='User Data', current_song='tito')


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(port='8888')  # testing this out. if this causes an issue uncomment above app.run(...) and delete this
    app.run(debug=True)
