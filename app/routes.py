from app import app, mysql
from flask import render_template, jsonify, request

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/admin-areas')
def adminareas():
    return render_template('admin-areas.html')

@app.route('/cajero')
def cajero():
    return render_template('cajero.html')

@app.route('/tutor')
def tutor():
    return render_template('tutor.html')

@app.route('/inscripcion')
def inscripcion():
    return render_template('inscripcion.html')

@app.route('/admin-reportes')
def adminreportes():
    return render_template('admin-reportes.html')

@app.route('/admin-competencia')
def admincompetencia():
    return render_template('admin-competencia.html')

@app.route('/inscribirse')
def inscribirse():
    return render_template('form-competidor.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/registrarse')
def registrarse():
    return render_template('registro.html')