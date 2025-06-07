from datetime import date, datetime
import locale
import traceback
from app import app, mysql
from flask import render_template, jsonify, request, redirect, url_for, session, flash
from functools import wraps
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus.tables import TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from flask import make_response

locale.setlocale(locale.LC_TIME, 'es_ES.utf8')

# Decoradores para proteger rutas según el tipo de usuario
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Inicia sesión para acceder a esta página', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session['rol'] != 'administrador':
            flash('No tienes permisos para acceder a esta página', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def cajero_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session['rol'] != 'cajero':
            flash('No tienes permisos para acceder a esta página', 'error')
            return redirect(url_for('home'))
        
        permitido, mensaje, _, _ = verificar_periodo('pagos')
        if not permitido:
            flash(mensaje, 'warning')
            return redirect(url_for('home'))
            
        return f(*args, **kwargs)
    return decorated_function

def tutor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session['rol'] != 'tutor':
            flash('No tienes permisos para acceder a esta página', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/competidor')
def competidor():
    # Verificar si el usuario ha iniciado sesión como competidor
    if 'competidor_id' not in session or 'rol' not in session or session['rol'] != 'competidor':
        flash('Debe iniciar sesión como competidor para acceder a esta página', 'error')
        return redirect(url_for('login'))
    
    # Obtener los datos del competidor
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_competidor, nombre, apellido, estado FROM competidor WHERE id_competidor = %s", 
                  [session['competidor_id']])
    competidor_data = cursor.fetchone()
    
    if not competidor_data:
        flash('Error al cargar los datos del competidor', 'error')
        return redirect(url_for('login'))
    
    # Obtener las competencias en las que está inscrito el competidor
    cursor.execute("""
        SELECT c.id_competencia, c.area, c.categoria, c.grado
        FROM competencia c 
        JOIN compite cm ON c.id_competencia = cm.id_competencia 
        WHERE cm.id_competidor = %s
    """, [session['competidor_id']])
    competencias = cursor.fetchall()
    
    #Obtener mensaje de estado
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM inscripcion WHERE id_competidor = %s", [session['competidor_id']])
    mensaje_data = cursor.fetchone()
    print("Mensaje de estado:", mensaje_data)

    return render_template('competidor.html', competidor=competidor_data, competencias=competencias, mensaje=mensaje_data)

def competidor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'competidor_id' not in session or 'rol' not in session or session['rol'] != 'competidor':
            flash('Debe iniciar sesión como competidor para acceder a esta página', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def verificar_periodo(tipo_periodo):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT fecha_inicio, fecha_fin FROM periodos_competencia WHERE tipo_periodo = %s", (tipo_periodo,))
        periodo = cursor.fetchone()
        cursor.close()
        
        if not periodo or not periodo['fecha_inicio'] or not periodo['fecha_fin']:
            return (False, f"No hay período de {tipo_periodo} configurado", None, None)
        
        hoy = datetime.now().date()
        inicio = periodo['fecha_inicio']
        fin = periodo['fecha_fin']
        
        if hoy < inicio:
            return (False, f"El período de {tipo_periodo} comenzará el {inicio.strftime('%d/%m/%Y')}",inicio, fin)
        elif hoy > fin:
            return (False, f"El período de {tipo_periodo} finalizó el {fin.strftime('%d/%m/%Y')}", inicio, fin)
        else:
            return (True, f"Estamos en período de {tipo_periodo}", inicio, fin)
            
    except Exception as e:
        print(f"Error al verificar periodo: {str(e)}")
        return (True, "Error al verificar período",None,None)

# Decorador para restringir por periodo
def periodo_requerido(tipo_periodo):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            permitido, mensaje, inicio, fin = verificar_periodo(tipo_periodo)
            if not permitido and "fuera de periodo" in mensaje:
                flash(mensaje, 'warning')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def home():
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM periodos_competencia"
    cursor.execute(sql)
    data = cursor.fetchall()

    # Procesar y formatear las fechas
    periodos = []
    for row in data:
        fecha_inicio = row['fecha_inicio'].strftime('%d de %B, %Y')
        fecha_fin = row['fecha_fin'].strftime('%d de %B, %Y')
        periodos.append({
            'tipo_periodo': row['tipo_periodo'],
            'fecha_inicio_formateada': fecha_inicio,
            'fecha_fin_formateada': fecha_fin
        })

    return render_template('home.html', periodos=periodos)

@app.route('/admin-areas')
@admin_required
def adminareas():
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM competencia"
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    return render_template('admin-areas.html', data=data)

@app.route('/cajero')
@cajero_required
def cajero():
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM competidor, compite, competencia WHERE estado = 'validado' and competidor.id_competidor = compite.id_competidor and competencia.id_competencia = compite.id_competencia"
    cursor.execute(sql)
    data = cursor.fetchall()
    
    return render_template('cajero.html', data=data)

@app.route('/confirmar-pago', methods=['POST'])
@cajero_required
@periodo_requerido('pagos')
def confirmar_pago():
    try:
        id_competidor = request.form['id_competidor']
        print("ID Competidor:", id_competidor)
        cursor = mysql.connection.cursor()
        sql = "UPDATE competidor SET estado = 'registrado' WHERE id_competidor = %s"
        cursor.execute(sql, (id_competidor,))
        mysql.connection.commit()
        
        flash('Pago confirmado correctamente', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al confirmar el pago: {str(e)}', 'danger')
    
    return redirect(url_for('cajero'))


@app.route('/tutor')
@tutor_required
def tutor():
    permitido, mensaje, _, _ = verificar_periodo('validacion')

    # Obtener el ID del tutor de la sesión
    tutor_id = session.get('tutor_id')
    cursor = mysql.connection.cursor()
    sql = "SELECT * from competidor WHERE id_tutor = %s and estado = 'pendiente'"
    sql2 = "SELECT * from competidor WHERE id_tutor = %s and estado = 'registrado'"
    cursor.execute(sql, (tutor_id,))
    data = cursor.fetchall() 
    cursor.execute(sql2, (tutor_id,))
    data2 = cursor.fetchall()   
    return render_template('tutor.html', data=data, data2=data2, periodo_activo=permitido, mensaje_periodo=mensaje)

@app.route('/validar-competidor', methods=['POST'])
@tutor_required
@periodo_requerido('validacion')
def validar_competidor():
    # Verificar primero si estamos en período de validación
    permitido, mensaje, _, _ = verificar_periodo('validacion')
    if not permitido:
        flash(mensaje, 'warning')
        return redirect(url_for('tutor'))

    try:
        id_competidor = request.form['id_competidor']
        print("ID Competidor:", id_competidor)
        cursor = mysql.connection.cursor()
        sql = "UPDATE competidor SET estado = 'validado' WHERE id_competidor = %s"
        cursor.execute(sql, (id_competidor,))
        mysql.connection.commit()
        
        flash('Competidor validado correctamente', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al validar el competidor: {str(e)}', 'danger')
    
    return redirect(url_for('tutor'))

@app.route('/admin-reportes')
@admin_required
def adminreportes():
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM competidor WHERE estado = 'registrado'"
    cursor.execute(sql)
    data = cursor.fetchall()
    num_competidores = len(data)
    return render_template('admin-reportes.html', num_competidores=num_competidores)

#@app.route('/admin-competencia')
#@admin_required
#def admincompetencia():
#    return render_template('admin-competencia.html')

@app.route('/inscribirse')
@periodo_requerido('inscripcion')
def inscribirse():
    
    render_template('form-competidor.html')
    permitido, mensaje, inicio, fin = verificar_periodo('inscripcion')
    if not permitido:
        flash(mensaje, 'warning')
        return redirect(url_for('home'))
    
    en_competencia, msg_comp, _, _ = verificar_periodo('competencia')
    if en_competencia and "En período" in msg_comp:
        flash('No se puede inscribir durante la competencia', 'danger')
        return redirect(url_for('home'))
    
    return render_template('form-competidor.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        
        # Validar formato de correo electrónico
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Formato de correo electrónico inválido', 'error')
            return render_template('login.html')
        
        contrasenia = request.form['password']
        cursor = mysql.connection.cursor()
        
        # Intentar encontrar el usuario en la tabla usuario
        cursor.execute("SELECT * FROM usuario WHERE email = %s", [email])
        user = cursor.fetchone()
        
        if user:
            if user['contrasenia'] != contrasenia:
                flash('Contraseña incorrecta', 'error')
                return render_template('login.html')
            
            session['user_id'] = user['id_usuario']
            session['nombre'] = user['nombre']
            session['apellido'] = user['apellido']
            session['email'] = user['email']
            session['rol'] = user['rol']
            
            if user['rol'] == 'administrador':
                cursor.execute("SELECT id_administrador FROM administrador WHERE id_usuario = %s", [user['id_usuario']])
                admin = cursor.fetchone()
                if admin:
                    session['admin_id'] = admin['id_administrador']
                return redirect(url_for('admincompetencia'))

            elif user['rol'] == 'cajero':
                cursor.execute("SELECT id_cajero FROM cajero WHERE id_usuario = %s", [user['id_usuario']])
                cajero = cursor.fetchone()
                if cajero:
                    session['cajero_id'] = cajero['id_cajero']
                return redirect(url_for('cajero'))

            elif user['rol'] == 'tutor':
                cursor.execute("SELECT id_tutor FROM tutor WHERE id_usuario = %s", [user['id_usuario']])
                tutor = cursor.fetchone()
                if tutor:
                    session['tutor_id'] = tutor['id_tutor']
                return redirect(url_for('tutor'))

            flash('Tipo de usuario no identificado', 'error')
            return redirect(url_for('login'))
        else:
            # Si no se encontró en usuario, buscar en competidor
            cursor.execute("SELECT * FROM competidor WHERE email = %s", [email])
            competidor = cursor.fetchone()

            if competidor:
                # Validar usando el campo 'ci' como contraseña
                if str(competidor['ci']) == contrasenia:
                    session['competidor_id'] = competidor['id_competidor']
                    session['nombre'] = competidor['nombre']
                    session['apellido'] = competidor['apellido']
                    session['email'] = competidor['email']
                    session['rol'] = 'competidor'  # Agregar el rol para validaciones
                    return redirect('/competidor')
                else:
                    flash('Contraseña incorrecta', 'error')
                    return render_template('login.html')
            else:
                # Si no se encontró en ninguna tabla
                flash('Usuario no encontrado', 'error')
                return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Eliminar todas las variables de sesión
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('home'))

@app.route('/registrarse', methods=['GET', 'POST'])
def registrarse():
    if request.method == 'POST':
        try:
            nombres = request.form.get('nombres', '').strip()
            apellidos = request.form.get('apellidos', '').strip()
            fecha_nacimiento = request.form.get('fechaNacimiento', '').strip()
            ci = request.form.get('ci', '').strip()
            email = request.form.get('email', '').strip()
            telefono = request.form.get('numCelular', '').strip()
            rol = request.form.get('rol', '').strip()
            contrasena = request.form.get('password', '').strip()

            cursor = mysql.connection.cursor()

            query_usuario = """
                INSERT INTO usuario (nombre, apellido, email, telefono, contrasenia, rol)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_usuario, (nombres, apellidos, email, telefono, contrasena, rol))
            usuario_id = cursor.lastrowid

            if rol == 'cajero':
                query_cajero = "INSERT INTO cajero (id_usuario) VALUES (%s)"
                cursor.execute(query_cajero, (usuario_id,))

            elif rol == 'tutor':
                tipo_tutor = request.form.get('tipoTutor', '').strip()
                area = request.form.get('area', '').strip()

                if not tipo_tutor or not area:
                    raise ValueError('Faltan datos de tutor: tipo_tutor o área.')

                query_tutor = "INSERT INTO tutor (id_usuario, tipo_tutor, area) VALUES (%s, %s, %s)"
                cursor.execute(query_tutor, (usuario_id, tipo_tutor, area))

            elif rol == 'administrador':
                query_administrador = "INSERT INTO administrador (id_usuario) VALUES (%s)"
                cursor.execute(query_administrador, (usuario_id,))

            mysql.connection.commit()
            cursor.close()

            flash('Usuario registrado correctamente.', 'success')
            return redirect(url_for('registrarse'))

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Ocurrió un error al registrar el usuario: {str(e)}', 'danger')
            return redirect(url_for('registrarse'))

    return render_template('registro.html')


# Ruta para obtener las competencias disponibles
@app.route('/obtener_competencias')
def obtener_competencias():
    try:
        cursor = mysql.connection.cursor()
        
        # Consulta SQL para obtener las competencias
        query = """
        SELECT id_competencia, area, categoria, grado
        FROM Competencia
        """
        
        cursor.execute(query)
        competencias = cursor.fetchall()
        cursor.close()
        
        # Convertir los resultados a una lista de diccionarios - VERSIÓN CORREGIDA
        resultado = []
        for comp in competencias:
            resultado.append({
                'id_competencia': comp['id_competencia'],
                'area': comp['area'],
                'categoria': comp['categoria'],
                'grado': comp['grado']
            })
        
        return jsonify(resultado)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta para registrar un nuevo competidor
@app.route('/registrar_competidor', methods=['POST'])
def registrar_competidor():
    if request.method == 'POST':
        try:
            # Obtener los datos del formulario
            nombre = request.form.get('nombre', '').strip()
            apellido = request.form.get('apellido', '').strip()
            fecha_nacimiento = request.form.get('fecha_nacimiento', '').strip()
            ci = request.form.get('ci', '').strip()
            email = request.form.get('email', '').strip()
            telefono = request.form.get('telefono', '').strip()
            colegio = request.form.get('colegio', '').strip()
            curso = request.form.get('curso', '').strip()
            departamento = request.form.get('departamento', '').strip()
            provincia = request.form.get('provincia', '').strip()
            area = request.form.get('area', '').strip()
            categoria = request.form.get('categoria', '').strip()
            id_tutor = request.form.get('id_tutor', '').strip()
            estado = 'pendiente'
            
            # Validar datos importantes
            if not nombre or not apellido or not ci or not email or not id_tutor:
                flash('Faltan datos obligatorios. Por favor completa todos los campos requeridos.', 'danger')
                return redirect(url_for('inscribirse'))
            
            #print(f"Datos recibidos: {nombre}, {apellido}, {fecha_nacimiento}, {curso}, {area}, {categoria}, {id_tutor}")
            cursor = mysql.connection.cursor()

             # 1. Validar que el CI esté asociado al mismo nombre, apellido y fecha si ya existe
            cursor.execute("""
                SELECT id_competidor 
                FROM Competidor 
                WHERE ci = %s 
                AND (nombre != %s OR apellido != %s OR fecha_nacimiento != %s)
            """, (ci, nombre, apellido, fecha_nacimiento))

            if cursor.fetchone():
                flash('Este número de carnet ya está registrado para otro competidor (con diferente nombre, apellido o fecha de nacimiento).', 'danger')
                return redirect(url_for('inscribirse'))
            
            # 2. Validar que no esté registrado en más de 2 competencias (usando CI o nombre+apellido+fecha)
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM Competidor c
                JOIN compite cm ON c.id_competidor = cm.id_competidor
                WHERE c.ci = %s 
                AND c.nombre = %s 
                AND c.apellido = %s 
                AND c.fecha_nacimiento = %s
            """, (ci, nombre, apellido, fecha_nacimiento))
            
            count = cursor.fetchone()['count']
            if count >= 2:
                flash('Este competidor ya está registrado en 2 competencias. No puede inscribirse en más.', 'danger')
                return redirect(url_for('inscribirse'))
            
            # 3. Verificar si el competidor ya existe para reutilizar o crear nuevo
            cursor.execute("""
                SELECT id_competidor 
                FROM Competidor 
                WHERE ci = %s 
                AND nombre = %s 
                AND apellido = %s 
                AND fecha_nacimiento = %s
            """, (ci, nombre, apellido, fecha_nacimiento))
            
            competidor_existente = cursor.fetchone()
            
            if competidor_existente:
                id_competidor = competidor_existente['id_competidor']
                
                # Actualizar datos del competidor si es necesario (manteniendo estado pendiente)
                update_competidor = """
                UPDATE Competidor 
                SET colegio = %s, curso = %s, departamento = %s, provincia = %s, 
                    email = %s, telefono = %s, estado = %s, id_tutor = %s
                WHERE id_competidor = %s
                """
                cursor.execute(update_competidor, (colegio, curso, departamento, provincia, 
                                                email, telefono, estado, id_tutor, 
                                                id_competidor))
            
            
            # 1. Insertar el competidor en la tabla Competidor
            insert_competidor = """
            INSERT INTO Competidor (ci, fecha_nacimiento, colegio, curso, departamento, provincia, 
                                  nombre, apellido, email, telefono, estado, id_tutor)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_competidor, (ci, fecha_nacimiento, colegio, curso, departamento, provincia, 
                                             nombre, apellido, email, telefono, estado, id_tutor))
            print("Competidor insertado correctamente")
            
            # Obtener el ID del competidor recién insertado
            id_competidor = cursor.lastrowid
            
            # 2. Crear una inscripción asociando el competidor con el tutor
            insert_inscripcion = """
            INSERT INTO Inscripcion (id_competidor, id_tutor, fecha_inscripcion)
            VALUES (%s, %s, %s)
            """
            fecha_actual = date.today()
            cursor.execute(insert_inscripcion, (id_competidor, id_tutor, fecha_actual))
            
            # 3. Obtener el ID de la competencia según el área, categoría y curso seleccionados
            query_competencia = """
            SELECT id_competencia FROM Competencia
            WHERE area = %s AND categoria = %s AND grado = %s
            """
            cursor.execute(query_competencia, (area, categoria, curso))
            competencia = cursor.fetchone()
            
            if competencia:
                id_competencia = competencia['id_competencia']  # Acceder como diccionario
                
                # Registrar la participación del competidor en la competencia
                insert_compite = """
                INSERT INTO compite (id_competencia, id_competidor)
                VALUES (%s, %s)
                """
                cursor.execute(insert_compite, (id_competencia, id_competidor))
            else:
                mysql.connection.rollback()
                cursor.close()
                flash('No se encontró la competencia seleccionada. Por favor verifica los datos.', 'danger')
                return redirect(url_for('inscribirse'))
            
            # 4. Establecer la relación entre el tutor y el competidor en la tabla "Puede tener"
            # Comentando esta parte porque puede que esta tabla no sea necesaria si ya tienes id_tutor en la tabla competidor
            # o si ya tienes la tabla inscripción que relaciona ambos
            """
            insert_puede_tener = """
            """INSERT INTO `Puede tener` (id_tutor, id_competidor)
            VALUES (%s, %s)
            """
            """
            cursor.execute(insert_puede_tener, (id_tutor, id_competidor))
            """
            # Confirmar los cambios en la base de datos
            mysql.connection.commit()
            cursor.close()
            
            flash('¡Inscripción realizada con éxito! Tu registro está pendiente de validación por el tutor.', 'success')
            # Redirigir a una página de éxito o a la página principal
            return redirect(url_for('inscribirse', inscripcion_exitosa='1'))
        
        except Exception as e:
            # En caso de error, hacer rollback y mostrar mensaje de error
            mysql.connection.rollback()
            print(f'Error en el registro: {str(e)}')
            flash(f'Error al registrar competidor: {str(e)}', 'danger')
            return redirect(url_for('inscribirse'))
    
    # Si la solicitud no es POST, redirigir a la página principal
    return redirect(url_for('home'))

@app.route('/obtener_tutores')
def obtener_tutores():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id_usuario, nombre, apellido FROM Usuario WHERE rol = 'tutor'")
        tutores = cursor.fetchall()
        cursor.close()
        
        return jsonify(tutores)
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    
@app.route('/obtener_tutores_completos')
def obtener_tutores_completos():
    try:
        # Crear un cursor para ejecutar consultas SQL
        cursor = mysql.connection.cursor()
        
        # Consulta SQL para obtener todos los datos de los tutores
        # Ahora incluye el id_tutor de la tabla de tutores
        cursor.execute("""
            SELECT u.id_usuario, t.id_tutor, u.nombre, u.apellido, u.email, u.telefono 
            FROM Usuario u
            INNER JOIN tutor t ON u.id_usuario = t.id_usuario
            WHERE u.rol = 'tutor'
        """)
        
        # Obtener los resultados
        tutores_raw = cursor.fetchall()
        
        # Convertir los resultados a una lista de diccionarios
        tutores = []
        for tutor in tutores_raw:
            tutores.append({
                'id_usuario': tutor['id_usuario'],
                'id_tutor': tutor['id_tutor'],
                'nombre': tutor['nombre'],
                'apellido': tutor['apellido'],
                'email': tutor['email'],
                'telefono': tutor['telefono']
            })
        
        # Cerrar el cursor
        cursor.close()
        
        return jsonify(tutores)
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    
@app.route('/registrar-area', methods=['POST'])
@admin_required
def registrar_area():
    data = {}
    data['curso'] = request.form['curso']
    data['area'] = request.form['area']
    data['categoria'] = request.form['categoria']
    data['costo'] = request.form['costo']

    cursor = mysql.connection.cursor()
    sql = "INSERT INTO competencia (area, categoria, grado, costo) VALUES (%s, %s, %s, %s)" 
    cursor.execute(sql, (data['area'], data['categoria'], data['curso'], data['costo']))
    mysql.connection.commit()
    cursor.close()
    flash('Área registrada correctamente', 'success')
    return redirect(url_for('adminareas'))

@app.route('/eliminar-comptencia', methods=['POST'])
@admin_required
def eliminar_competencia():
    data = {}
    data['id'] = request.form['id']
    
    cursor = mysql.connection.cursor()
    sql = "DELETE FROM competencia WHERE id_competencia = %s" 
    cursor.execute(sql, (data['id'],))
    mysql.connection.commit()
    cursor.close()
    flash('Competencia eliminada correctamente', 'success')
    return redirect(url_for('adminareas'))

#esta funcion bloquea todas las demas mientras se esta en el periodo de competicion
@app.before_request
def verificar_fecha_sistema():
    # Excluir rutas que deben estar disponibles siempre
    excluded_routes = ['login', 'logout', 'home', 'static', 'admincompetencia']
    if request.endpoint in excluded_routes:
        return
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT fecha_inicio, fecha_fin FROM periodos_competencia WHERE tipo_periodo = 'competencia'")
        competencia = cursor.fetchone()
        cursor.close()
        
        if competencia:
            hoy_sistema = datetime.now().date()
            inicio_competencia = competencia['fecha_inicio']
            fin_competencia = competencia['fecha_fin']
            
            if inicio_competencia <= hoy_sistema <= fin_competencia:
                flash('El sistema está en período de competencia. Acciones restringidas.', 'danger')
                return redirect(url_for('home'))
    except Exception as e:
        print(f"Error al verificar fecha del sistema: {str(e)}")



# Ruta para mostrar el formulario con las fechas actuales
@app.route('/admin-competencia', methods=['GET', 'POST'])
@admin_required
def admincompetencia():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM periodos_competencia")
    periodos = cursor.fetchall()

    fechas = {
        'inscripcion': {'inicio': '', 'fin': ''},
        'validacion': {'inicio': '', 'fin': ''},
        'pagos': {'inicio': '', 'fin': ''},
        'competencia': {'inicio': '', 'fin': ''}
    }

    for p in periodos:
        if p['fecha_inicio']:
            fecha_inicio = p['fecha_inicio'].strftime('%Y-%m-%d') if isinstance(p['fecha_inicio'], (date, datetime)) else ''
            fechas[p['tipo_periodo']]['inicio'] = fecha_inicio

        if p['fecha_fin']:
            fecha_fin = p['fecha_fin'].strftime('%Y-%m-%d') if isinstance(p['fecha_fin'], (date, datetime)) else ''
            fechas[p['tipo_periodo']]['fin'] = fecha_fin

    if request.method == 'POST':
        try:
            periodos_form = {
                'inscripcion': {'inicio': 'fechaIniIns', 'fin': 'fechaFinIns'},
                'validacion': {'inicio': 'fechaIniVal', 'fin': 'fechaFinVal'},
                'pagos': {'inicio': 'fechaIniPag', 'fin': 'fechaFinPag'},
                'competencia': {'inicio': 'fechaIniComp', 'fin': 'fechaFinComp'}
            }

            for tipo, campos in periodos_form.items():
                fecha_inicio_str = request.form.get(campos['inicio'])
                fecha_fin_str = request.form.get(campos['fin'])

                if fecha_inicio_str and fecha_fin_str:
                    try:
                        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()

                        if fecha_fin < fecha_inicio:
                            flash(f'Error en {tipo}: La fecha fin no puede ser menor que la fecha inicio', 'danger')
                            continue

                        cursor.execute("""
                            INSERT INTO periodos_competencia (tipo_periodo, fecha_inicio, fecha_fin)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                                fecha_inicio = VALUES(fecha_inicio),
                                fecha_fin = VALUES(fecha_fin)
                        """, (tipo, fecha_inicio, fecha_fin))

                        fechas[tipo]['inicio'] = fecha_inicio_str
                        fechas[tipo]['fin'] = fecha_fin_str

                    except ValueError:
                        flash(f'Formato de fecha inválido para {tipo}', 'danger')

            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('admincompetencia', exito=1))  # 🔁 Redirección con parámetro

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al actualizar fechas: {str(e)}', 'danger')
            cursor.close()
            return render_template('admin-competencia.html', fechas=fechas, exito=False)

    # 👇 Detectar si viene el parámetro "exito" para mostrar el modal
    exito = request.args.get('exito') == '1'
    cursor.close()
    return render_template('admin-competencia.html', fechas=fechas, exito=exito)

@app.route('/generar-reporte-pdf', methods=['POST'])
@admin_required
def generar_reporte_pdf():
    grado = request.form['grado'].strip()
    print("Grado recibido:", grado)  

    cursor = mysql.connection.cursor()

    if grado == "todos_estados":
        sql = """
            SELECT nombre, apellido, ci, colegio, departamento, provincia, email, telefono, estado, curso
            FROM competidor
            ORDER BY estado, curso, nombre, apellido
        """
        cursor.execute(sql)
    elif grado == "todos":
        sql = """
            SELECT nombre, apellido, ci, colegio, departamento, provincia, email, telefono, estado, curso
            FROM competidor
            WHERE estado = 'registrado'
        """
        cursor.execute(sql)
    else:
        sql = """
            SELECT nombre, apellido, ci, colegio, departamento, provincia, email, telefono, estado, curso
            FROM competidor
            WHERE LOWER(REPLACE(curso, ' ', '')) = LOWER(REPLACE(%s, ' ', ''))
            AND estado = 'registrado'
        """
        cursor.execute(sql, (grado,))

    data = cursor.fetchall()
    cursor.close()

    print(f"Total filas recuperadas: {len(data)}")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        leftMargin=20,
        rightMargin=20,
        topMargin=30,
        bottomMargin=30
    )
    styles = getSampleStyleSheet()
    elements = []

    if grado == "todos_estados":
        titulo = "Reporte Completo - Todos los Competidores"
    elif grado == "todos":
        titulo = "Reporte de Competidores - Todos los Niveles"
    else:
        titulo = f"Reporte de Competidores - Nivel: {grado}"
    
    elements.append(Paragraph(titulo, styles['Title']))
    elements.append(Spacer(1, 12))

    if grado in ["todos_estados", "todos"]:
        table_data = [[
            'Nombre', 'Apellido', 'CI', 'Curso', 'Colegio',
            'Departamento', 'Provincia', 'Email', 'Teléfono', 'Estado'
        ]]
    else:
        table_data = [[
            'Nombre', 'Apellido', 'CI', 'Colegio',
            'Departamento', 'Provincia', 'Email', 'Teléfono', 'Estado'
        ]]

    if data:
        for row in data:
            if grado in ["todos_estados", "todos"]:
                table_data.append([
                    str(row['nombre']) if row['nombre'] is not None else '',
                    str(row['apellido']) if row['apellido'] is not None else '',
                    str(row['ci']) if row['ci'] is not None else '',
                    str(row['curso']) if row['curso'] is not None else '',
                    str(row['colegio']) if row['colegio'] is not None else '',
                    str(row['departamento']) if row['departamento'] is not None else '',
                    str(row['provincia']) if row['provincia'] is not None else '',
                    str(row['email']) if row['email'] is not None else '',
                    str(row['telefono']) if row['telefono'] is not None else '',
                    str(row['estado']) if row['estado'] is not None else ''
                ])
            else:
                table_data.append([
                    str(row['nombre']) if row['nombre'] is not None else '',
                    str(row['apellido']) if row['apellido'] is not None else '',
                    str(row['ci']) if row['ci'] is not None else '',
                    str(row['colegio']) if row['colegio'] is not None else '',
                    str(row['departamento']) if row['departamento'] is not None else '',
                    str(row['provincia']) if row['provincia'] is not None else '',
                    str(row['email']) if row['email'] is not None else '',
                    str(row['telefono']) if row['telefono'] is not None else '',
                    str(row['estado']) if row['estado'] is not None else ''
                ])
    else:
        if grado == "todos_estados":
            mensaje = 'No hay competidores en el sistema'
        elif grado == "todos":
            mensaje = 'No hay competidores registrados'
        else:
            mensaje = f'No hay competidores registrados para {grado}'
        
        num_columnas = 10 if grado in ["todos_estados", "todos"] else 9
        table_data.append([mensaje] + [''] * (num_columnas - 1))

    table = Table(table_data, repeatRows=1)
    
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),  
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),   
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),            
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  
        ('FONTSIZE', (0, 0), (-1, -1), 7),              
        ('BACKGROUND', (0, 1), (-1, -1), colors.white), 
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),            
    ]
    
    table.setStyle(TableStyle(table_style))
    elements.append(table)

    doc.build(elements)

    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    accion = request.form.get('accion', 'descargar')
    disposition_type = 'inline' if accion == 'visualizar' else 'attachment'
    
    if grado == "todos_estados":
        nombre_archivo = "Reporte_Completo_Todos_Estados.pdf"
    elif grado == "todos":
        nombre_archivo = "Reporte_Todos_Niveles_Registrados.pdf"
    else:
        nombre_archivo = f"Reporte_{grado.replace(' ', '_')}.pdf"
    
    response.headers['Content-Disposition'] = f'{disposition_type}; filename={nombre_archivo}'

    return response

# Funcion del motivo por el cual fue rechazado el tutor
@app.route('/rechazar_competidor', methods=['POST'])
@tutor_required
def rechazar_competidor():
    try:
        id_competidor = request.form['id_competidor']
        mensaje = request.form['motivo']  

        cursor = mysql.connection.cursor()

        sql_estado = "UPDATE competidor SET estado = 'rechazado' WHERE id_competidor = %s"
        cursor.execute(sql_estado, (id_competidor,))

        sql_mensaje = "UPDATE inscripcion SET mensaje = %s WHERE id_competidor = %s"
        cursor.execute(sql_mensaje, (mensaje, id_competidor))

        mysql.connection.commit()

        flash('Competidor rechazado con mensaje registrado', 'info')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al rechazar el competidor: {str(e)}', 'danger')
    
    return redirect(url_for('tutor'))

@app.route('/obtener_tutores_por_area/<string:area>')
def obtener_tutores_por_area(area):
    try:
        # Crear un cursor para ejecutar consultas SQL
        cursor = mysql.connection.cursor()
        
        # Consulta SQL para obtener los tutores que pertenecen a un área específica
        cursor.execute("""
            SELECT u.id_usuario, t.id_tutor, u.nombre, u.apellido, u.email, u.telefono 
            FROM Usuario u
            INNER JOIN tutor t ON u.id_usuario = t.id_usuario
            WHERE u.rol = 'tutor' AND t.area = %s
        """, [area])
        
        # Obtener los resultados
        tutores_raw = cursor.fetchall()
        
        # Convertir los resultados a una lista de diccionarios
        tutores = []
        for tutor in tutores_raw:
            tutores.append({
                'id_usuario': tutor['id_usuario'],
                'id_tutor': tutor['id_tutor'],
                'nombre': tutor['nombre'],
                'apellido': tutor['apellido'],
                'email': tutor['email'],
                'telefono': tutor['telefono']
            })
        
        # Cerrar el cursor
        cursor.close()
        
        return jsonify(tutores)
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    
