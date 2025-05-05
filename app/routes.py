from app import app, mysql
from flask import flash, redirect, render_template, jsonify, request, url_for
from datetime import datetime
import hashlib


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
            INSERT INTO Competidor (ci, fecha_nacimiento, colegio, curso, departamento, provincia, nombre, apellido, email, telefono, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (ci, fecha_nacimiento, colegio, curso, departamento, provincia, nombres, apellidos, email, telefono, "pendiente"))

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
        cur.execute(
            "SELECT id_competencia FROM Competencia WHERE nombre = %s", (area,))
        resultado = cur.fetchone()
        if resultado:
            id_competencia = resultado[0]
            cur.execute("INSERT INTO Compite (id_competencia, id_competidor) VALUES (%s, %s)",
                        (id_competencia, id_competidor))

        mysql.connection.commit()
        flash('Inscripción guardada correctamente')
        return redirect(url_for('inscribirse'))

    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al procesar inscripción: {str(e)}')
        return redirect(url_for('inscribirse'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            nombres = request.form.get('nombres').strip()
            apellidos = request.form.get('apellidos').strip()
            fecha_nacimiento = request.form.get('fechaNacimiento')
            ci = request.form.get('ci').strip()
            email = request.form.get('email').strip()
            telefono = request.form.get('numCelular').strip()
            rol = request.form.get('rol').strip()
            contrasena = request.form.get('password').strip()

            hashed_password = hashlib.md5(contrasena.encode()).hexdigest()

            cursor = mysql.connection.cursor()

            cursor.execute("SELECT MAX(id_usuario) FROM usuario")
            max_id_usuario = cursor.fetchone()['MAX(id_usuario)'] or 0
            new_id_usuario = max_id_usuario + 1

            query_usuario = """
                INSERT INTO usuario (id_usuario, nombre, apellido, email, telefono, contrasenia, rol)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_usuario, (new_id_usuario, nombres,
                           apellidos, email, telefono, hashed_password, rol))
            mysql.connection.commit()

            if rol == 'Cajero':
                cursor.execute("SELECT MAX(id_cajero) FROM cajero")
                max_id_cajero = cursor.fetchone()['MAX(id_cajero)'] or 0
                new_id_cajero = max_id_cajero + 1

                query_cajero = "INSERT INTO cajero (id_cajero, id_usuario) VALUES (%s, %s)"
                cursor.execute(query_cajero, (new_id_cajero, new_id_usuario))

            elif rol == 'Tutor':
                cursor.execute("SELECT MAX(id_tutor) FROM tutor")
                max_id_tutor = cursor.fetchone()['MAX(id_tutor)'] or 0
                new_id_tutor = max_id_tutor + 1

                tipo_tutor = "Profesor"  
                query_tutor = "INSERT INTO tutor (id_tutor, id_usuario, tipo_tutor) VALUES (%s, %s, %s)"
                cursor.execute(query_tutor, (new_id_tutor,
                               new_id_usuario, tipo_tutor))

            elif rol == 'Administrador':
                cursor.execute(
                    "SELECT MAX(id_administrador) FROM administrador")
                max_id_administrador = cursor.fetchone()[
                    'MAX(id_administrador)'] or 0
                new_id_administrador = max_id_administrador + 1

                query_administrador = "INSERT INTO administrador (id_administrador, id_usuario) VALUES (%s, %s)"
                cursor.execute(query_administrador,
                               (new_id_administrador, new_id_usuario))

            mysql.connection.commit()
            cursor.close()

            flash('Usuario registrado correctamente.', 'success')
            return redirect(url_for('register'))

        except Exception as e:
            mysql.connection.rollback()
            flash(
                f'Ocurrió un error al registrar el usuario: {str(e)}', 'danger')
            return redirect(url_for('register'))

    return render_template('auth/register.html')
