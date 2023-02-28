# server
from flask_bcrypt import Bcrypt
from flask import Flask, jsonify, request, render_template, session, redirect, url_for, g
from flask_cors import CORS
# requests
import os
import json
import requests
# session voodoo magic
from flask_session import Session

PORT = 8080

# app config
app = Flask(__name__, static_url_path='', static_folder='static')
app.secret_key = os.urandom(24)
CORS(app)
bcrypt = Bcrypt(app)

@app.route('/submit', methods=['POST'])
def submit():
    typex = request.form.get('type')
    participants = request.form.get('participants')
    price = request.form.get('price')
    accessibility = request.form.get('accessibility')
    url = 'http://www.boredapi.com/api/activity?type={}&participants{}&price={}&accessibility={}'.format(typex, participants, price, accessibility)
    output = requests.request('GET', url).json()
    print(output)
    return render_template('activities.html', info=output)

@app.route('/quotes', methods=['POST'])
def quotes():
    category = request.form.get('category')
    print(category)
    url = 'https://api.api-ninjas.com/v1/quotes?category={}'.format(category)
    response = requests.get(url, headers={'X-Api-Key': 'API_KEY'})
    print(response.json())
    return render_template("quote.html", info=response.json())

@app.route('/', methods=['GET'])
def reroute_index():
    return redirect('index.html')

@app.route("/index.html")
def index():
    err_msg = request.args.get('err_msg', '')
    print(err_msg)
    return render_template("index.html", usr=g.user, err_msg=err_msg)

@app.route('/signup.html', methods=['POST'])
def sign_up_page_render():
    if g.user != None:
        return redirect('index.html')
    inp_uname = request.form.get('uname', None)
    inp_pass = request.form.get('pass', None)
    inp_email = request.form.get('email', None)
    if inp_uname == None or inp_pass == None or inp_email == None or len(inp_uname) < 5 or len(inp_pass) < 5:
        return redirect("/index.html?err_msg=bad signup input")
    #---- add account to database----
    # check if username taken
    dbr = open('db.json', 'r')
    db_obj = json.load(dbr)
    unames = [user['uname'] for user in db_obj['users']]
    emails = [user['email'] for user in db_obj['users']]
    for uname in unames:
        if inp_uname == uname:
            return redirect("/index.html?err_msg=username taken")
    for email in emails:
        if inp_email == email:
            return redirect("/index.html?err_msg=email used")
    # add user to database
    print('adding user now')
    print('name:' + request.form['uname'])
    db_obj["users"].append({
        "uname": request.form["uname"],
        "pass": str(bcrypt.generate_password_hash(inp_pass), encoding="utf-8"),
        "email": request.form["email"],
        "settings": {
            "quote-ping": True
        },
        "reminders": []
    })
    print(db_obj)
    dbr.close()
    # replace db
    # Write the dictionary to the JSON file
    with open("db.json", "w") as outfile:
        json.dump(db_obj, outfile, indent=4)
    session['user'] = inp_uname
    return redirect('/')

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

@app.route('/add_reminder', methods=["POST"])
def add_reminder():
    # get current user
    db = open('db.json', 'w')
    # add reminder here
    return

@app.route('/remove_reminder', methods=["POST"])
def remove_reminder():
    # get user
    db = open('db.json', 'w')
    # remove reminder from db by index

@app.route('/sign_out', methods=["GET", "POST"])
def sign_out():
    # session voodoo magic
    session.pop('user', None)
    return redirect(url_for('index'))
# @app.route('/updateSettings')
# def updateSettings():
#     return

@app.route("/signin.html", methods=["POST"])
def sign_in():
    if g.user != None:
        return redirect('index.html')
    inp_uname = request.form.get('uname', None)
    inp_pass = request.form.get('pass', None)
    if inp_uname == None or inp_pass == None:
        return redirect("/index.html?err_msg=bad signin input")
    #---- add account to database----
    # check for user
    dbr = open('db.json', 'r')
    db_obj = json.load(dbr)
    unames = [user for user in db_obj['users']]
    for i in range(len(unames)):
        uname = unames[i]["uname "]
        if inp_uname == uname:
            if bcrypt.check_password_hash(bytes(unames[i]["pass"], encoding="utf-8"), inp_pass):
                session['user'] = inp_uname
                return redirect("index.html")
    return redirect("index.html?err_msg=Bad login")
    
if __name__ == '__main__':
    print('connected on port ' + str(PORT))
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=True
    )