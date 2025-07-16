# Imports 
from flask import Flask, render_template, redirect, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import secrets
import requests
import json 

#app setup
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///snip-url.db"
db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String, nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    clicks = db.relationship('Click', backref='url', lazy=True)

class Click(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.Integer, db.ForeignKey('url.id'), nullable=False) #the id of URL
    clicked_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc)) #shows when it was clicked
    ip_address = db.Column(db.String(45)) 

def check_url_exists(url):
    try:
        response = requests.get(url)
        # A 2xx status code generally indicates success
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.ConnectionError:
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        #gets the URL and turn it into python dictionary
        data = request.get_json()
        #Turns url into the www.xyz.abc format
        original_url = data.get('original_url')

        #checks for user input and if input is a url
        if not original_url:
            return jsonify({"error": "Missing original_url"}), 400
        
        #validating url
        if not check_url_exists(original_url):
            return jsonify({"error": "URL does not exist"}), 400
        
        #Make the unique code
        short_code = secrets.token_urlsafe(6)[:6]
        while URL.query.filter_by(short_code=short_code).first():
            short_code = secrets.token_urlsafe(6)[:6]

        #To add URL to snip-url.db
        new_url = URL(original_url=original_url, short_code=short_code)
        db.session.add(new_url)
        db.session.commit()

        #Convert to json
        return jsonify({
            "short_url" : request.host_url + short_code
        }), 201
    return render_template('index.html')

@app.route('/<short_code>', methods = ['GET'])
def short_url(short_code):
    url = URL.query.filter_by(short_code=short_code).first()
    if not url:
        return jsonify({"error": "Short URL not found"}), 404

    click = Click(url_id=url.id, ip_address=request.remote_addr)
    db.session.add(click)
    db.session.commit()

    return redirect(url.original_url)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()   # Create tables here safely inside app context
    app.run(debug=True)

