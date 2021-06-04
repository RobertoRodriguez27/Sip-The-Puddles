from flask import Flask, render_template, json
import os
# from stocks import User
from personal.user_info import client_secret, client, username
from monthly import Rework

app = Flask(__name__)

# user = User(client_id=client, client_secret=client_secret, username=username)
re = Rework(client_id=client, client_secret_id=client_secret, username=username)


@app.route("/")
@app.route("/portfolio", methods=["GET"])
def home():
    artists_followers = re.rework_monthly()
    artist_labels = artists_followers['artists'].to_list()
    artist_data = artists_followers['monthly listeners'].to_list()
    return render_template("LandingPage.html", a_label=json.dumps(artist_labels), a_data=json.dumps(artist_data))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8989))
    app.run(debug=True, host='0.0.0.0', port=port)

