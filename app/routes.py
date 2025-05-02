from app import app, mysql
from flask import flash, redirect, render_template, jsonify, request, url_for
from datetime import datetime

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

@app.route('/procesar_inscripcion', methods=['POST'])
def procesar_inscripcion():
    try:
        # Obtener datos del formulario
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        fecha_nacimiento = request.form['fechaNacimiento']
        ci = request.form['ci']
        email = request.form['email']
        telefono = request.form['numCelular']
        colegio = request.form['colegio']
        curso = request.form['curso']
        provincia = request.form['provincia']
        departamento = request.form['departamento']
        area = request.form['area']
        categoria = request.form['categoría']
        id_tutor = request.form.get('tutor') or None  # Puede ser vacío

        cur = mysql.connection.cursor()

        # Insertar en tabla Competidor
        cur.execute("""
            INSERT INTO Competidor (ci, fecha_nacimiento, colegio, curso, departamento, provincia, nombre, apellido, email, telefono)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (ci, fecha_nacimiento, colegio, curso, departamento, provincia, nombres, apellidos, email, telefono))
        
        # Obtener el ID del competidor recién insertado
        mysql.connection.commit()
        id_competidor = cur.lastrowid

        # Insertar en tabla Inscripcion
        fecha_inscripcion = datetime.now().strftime('%Y-%m-%d')
        cur.execute("""
            INSERT INTO Inscripcion (id_competidor, id_tutor, fecha_inscripcion)
            VALUES (%s, %s, %s)
        """, (id_competidor, id_tutor, fecha_inscripcion))

        # Suponiendo que el área seleccionada representa una competencia:
        # Aquí deberías mapear 'area' a un ID de competencia válido.
        # Por ejemplo, usando una consulta para obtener `id_competencia`:
        cur.execute("SELECT id_competencia FROM Competencia WHERE nombre = %s", (area,))
        resultado = cur.fetchone()
        if resultado:
            id_competencia = resultado[0]
            cur.execute("INSERT INTO Compite (id_competencia, id_competidor) VALUES (%s, %s)", (id_competencia, id_competidor))
        
        mysql.connection.commit()
        flash('Inscripción guardada correctamente')
        return redirect(url_for('inscribirse'))

    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al procesar inscripción: {str(e)}')
        return redirect(url_for('inscribirse'))