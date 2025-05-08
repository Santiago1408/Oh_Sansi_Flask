from app import app, mysql
from flask import render_template, jsonify, request
from flask import render_template, request, redirect, url_for, flash
from datetime import date

datos_competencia = {
    "inscripcion": (),
    "validacion": (),
    "pago": (),
    "competencia": ()
}

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

@app.route('/admin-competencia', methods=['GET', 'POST'])
def admin_competencia():
    global datos_competencia
    fecha_hoy = date.today().isoformat()

    if request.method == 'POST':
        datos_competencia["inscripcion"] = (
            request.form.get('fechaIniIns'),
            request.form.get('fechaFinIns')
        )
        datos_competencia["validacion"] = (
            request.form.get('fechaIniVal'),
            request.form.get('fechaFinVal')
        )
        datos_competencia["pago"] = (
            request.form.get('fechaIniPag'),
            request.form.get('fechaFinPag')
        )
        datos_competencia["competencia"] = (
            request.form.get('fechaIniComp'),
            request.form.get('fechaFinComp')
        )

        flash("Fechas guardadas correctamente.", "success")
        return redirect(url_for('admin_competencia'))

    return render_template('admin-competencia.html', datos=datos_competencia, fecha_hoy=fecha_hoy)
