from app import app, mysql
from flask import render_template, jsonify

@app.route('/')
def home():
    return render_template('home.html')


