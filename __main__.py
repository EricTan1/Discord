from flask import Flask, request, render_template, redirect, session
from oauthBlizzard import Oauth

app = Flask(__name__)

@app.route("/", methods=["get"])
def index():
    return redirect(Oauth.blizzard_login_url)

@app.route("/login", methods=["get"])
def login():
    code = request.args.get("code")
    res = Oauth.get_access_token(code)
    r = Oauth.get_user_json(res.get("access_token"))
    
    return str(r) + str(res)


if(__name__ == "__main__"):
    app.run(debug=True)
    #serve(app, host='0.0.0.0', port=8080)
    
