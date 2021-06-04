from flask import Flask, render_template, json
# from flask_sockets import Sockets
import os
# from stocks import User
from personal.user_info import client_secret, client, username
from monthly import Rework

app = Flask(__name__)

# user = User(client_id=client, client_secret=client_secret, username=username)
# re = Rework(client_id=client, client_secret_id=client_secret, username=username)


@app.route("/")
# @app.route("/portfolio", methods=["GET"])
def home():
    return "Hello Heroku"
    # artists_followers = re.rework_monthly()
    # artist_labels = artists_followers['artists'].to_list()
    # artist_data = artists_followers['monthly listeners'].to_list()
    # return render_template("LandingPage.html", a_label=json.dumps(artist_labels), a_data=json.dumps(artist_data))


if __name__ == "__main__":
    # ON_HEROKU = os.environ.get('ON_HEROKU')
    # if ON_HEROKU:
    #     port = int(os.environ.get("PORT", 17995))
    # else:
    #     port = 3000
    # , host = '0.0.0.0', port = port
    app.run(debug=True)

