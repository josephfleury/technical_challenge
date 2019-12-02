from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import json
import os
import sqlite3
import sys

import requests
from db.db import init_db_command
from db.user import User
from flask import Flask, request, redirect, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from healthcheck import HealthCheck
from oauthlib.oauth2 import WebApplicationClient
from prometheus_client import start_wsgi_server as prometheus_server
from solver.solver import solver
from werkzeug.middleware.proxy_fix import ProxyFix

# Configuration
CONFIG_NAME_MAPPER = {
    'development': 'config/config.Development.cfg',
    'testing': 'config/config.Testing.cfg',
    'production': 'config/config.Production.cfg'
}

# Load Config
flask_config_name = os.environ.get("FLASK_CONFIG") or 'development'

# App config
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config.from_pyfile(CONFIG_NAME_MAPPER[flask_config_name])
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# User session management setup

login_manager = LoginManager()
login_manager.init_app(app)

# OAuth2 client setup
client = WebApplicationClient(app.config["GOOGLE_CLIENT_ID"])

# Naive database setup
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass


def health_check():
    return True, "OK"


# The root endpoint returns the application value. Some percentage of the time
# (given by application.config['failure_rate']) calls to this endpoint will cause the
# application to crash (exits non-zero).
@app.route('/v1/', methods=["GET"])
def index():
    input_val = json.loads(request.args.get("input"))
    result = solver(input_val)
    return result


# The root endpoint returns the application value. Some percentage of the time
# (given by application.config['failure_rate']) calls to this endpoint will cause the
# application to crash (exits non-zero).
@app.route('/v2/', methods=["POST"])
def indexV2():
    if current_user.is_authenticated:
        input_val = request.json
        result = solver(input_val)
        return result

    else:
        return '<a class="button" href="/login">Google Login</a>'


@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to access this content.", 403


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(app.config["GOOGLE_CLIENT_ID"], app.config["GOOGLE_CLIENT_SECRET"]),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # application, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in our db with the information provided
    # by Google
    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    # Doesn't exist? Add to database
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


def get_google_provider_cfg():
    return requests.get(app.config["GOOGLE_DISCOVERY_URL"]).json()


def main(args):
    prometheus_server(8081)

    app.config.update({
        'input': args.input,
        'crashed': False
    })

    health = HealthCheck()
    health.add_check(health_check)
    app.add_url_rule("/healthcheck", "healthcheck", view_func=lambda: health.run())

    app.run()

    if app.config['crashed']:
        print('application crashed, exiting non-zero')
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input',
        type=str,
        required=False,
        help='the input string'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='the serving port'
    )
    parser.add_argument(
        '--monitor',
        type=int,
        default=8081,
        help='the monitoring port'
    )
    return parser.parse_args()


if __name__ == '__main__':
    main(parse_args())
