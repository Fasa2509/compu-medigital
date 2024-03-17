from flask import Flask, jsonify, make_response, redirect, render_template, request
from dotenv import load_dotenv, dotenv_values
from flask_cors import CORS
import json

from src.errors.main import ApiErrorHandler, ParsingException
from src.helpers.dates import get_unix_now
from src.helpers.JWT import decode_jwt, encode_jwt
from src.database.main import db_injection, setUpDatabase
from src.custom_types.consulta import ConsultaFactoryDates, ConsultaFactoryInt
from src.custom_types.diagnostico import DiagnosticoFactoryDates
from src.custom_types.tratamiento import TratamientoFactoryDates
from src.custom_types.paciente import PacienteFactoryDates
from src.custom_types.administrativo import AdministrativoFactoryDates
from src.custom_types.medico import MedicoFactoryDates
from src.custom_types.Api import ApiResponse, ApiResponsePayload
from src.routes.api import usuario, paciente, medico, administrativo, consulta, diagnostico, tratamiento, contacto, reporte

# cargamos variables de entorno del archivo .env
load_dotenv()
config = dotenv_values(".env")


app = Flask(__name__)
CORS(app)

# registramos blueprint API de usuarios
usuario_api = app.register_blueprint(usuario.bp, url_prefix='/api/usuario')

# registramos blueprint API de pacientes
paciente_api = app.register_blueprint(paciente.bp, url_prefix='/api/paciente')

# registramos blueprint API de medicos
medicos_api = app.register_blueprint(medico.bp, url_prefix='/api/medico')

# registramos blueprint API de administrativos
administrativo_api = app.register_blueprint(
    administrativo.bp, url_prefix='/api/administrativo')

# registramos blueprint API de consultas
consulta_api = app.register_blueprint(consulta.bp, url_prefix='/api/consulta')

# registramos blueprint API de diagnosticos
diagnostico_api = app.register_blueprint(
    diagnostico.bp, url_prefix='/api/diagnostico')

# registramos blueprint API de tratamientos
tratamiento_api = app.register_blueprint(
    tratamiento.bp, url_prefix='/api/tratamiento')

# registramos blueprint API de tratamientos
contacto_api = app.register_blueprint(contacto.bp, url_prefix='/api/contacto')

# registramos blueprint API de historiales
historial_api = app.register_blueprint(reporte.bp, url_prefix='/api/reporte')


@app.route("/")
def index():
    token = request.cookies.get("auth-cookie")

    session = decode_jwt(token) if token else None

    if session:
        db = db_injection()

        cursor = db.cursor()

        usuario = cursor.execute(
            """SELECT
                id,
                nombre,
                clave,
                ci,
                telefono,
                correo,
                genero,
                nacimiento,
                fecha_creacion
                FROM usuario WHERE correo = (?)""", (session.get("correo"),)).fetchone()

        if not usuario:
            raise ParsingException(["No se encontró el usuario"])

        paciente = cursor.execute(
            """SELECT
            direccion,
            religion,
            sangre
            FROM paciente WHERE usuario_id = (?)""", (usuario[0],)).fetchone()

        medico = cursor.execute(
            """SELECT
            especialidad
            FROM medico WHERE usuario_id = (?)""", (usuario[0],)).fetchone()

        administrativo = cursor.execute(
            """SELECT
            oficina,
            medico_id
            FROM administrativo WHERE usuario_id = (?)""", (usuario[0],)).fetchone()

        db.close()

        if paciente:
            usuario = list(usuario)
            usuario.pop(2)
            usuario.extend(list(paciente))
            if usuario == None:
                raise ParsingException(["Error con el usuario"])
            usuario = PacienteFactoryDates(usuario)
        elif medico:
            usuario = list(usuario)
            usuario.pop(2)
            usuario.extend(list(medico))
            if usuario == None:
                raise ParsingException(["Error con el usuario"])
            usuario = MedicoFactoryDates(usuario)
        elif administrativo:
            usuario = list(usuario)
            usuario.pop(2)
            usuario.extend(list(administrativo))
            if usuario == None:
                raise ParsingException(["Error con el usuario"])
            usuario = AdministrativoFactoryDates(usuario)
        else:
            db.close()
            raise ParsingException(
                ["No se encontró información referente al usuario"])

        session = usuario

        res = make_response(render_template("index.html.j2", session=session))

        token = encode_jwt(usuario)

        res.set_cookie("auth-cookie", token, path="/", httponly=True)

        return res

    return render_template("index.html.j2", session=session)


@app.route("/login")
def login():
    token = request.cookies.get("auth-cookie")

    session = decode_jwt(token) if token else None

    if session or token:
        return redirect("/")

    return render_template("login.html.j2")


@app.route("/creditos")
def creditos():
    token = request.cookies.get("auth-cookie")

    session = decode_jwt(token) if token else None
    return render_template("creditos/index.html.j2", session=session)


@app.route("/medicos")
def medicos():
    token = request.cookies.get("auth-cookie")

    session = decode_jwt(token) if token else None

    db = db_injection()

    cursor = db.cursor()

    medicos = cursor.execute(
        """SELECT
        usuario.id as id,
        usuario.nombre as nombre,
        usuario.ci as ci,
        usuario.telefono as telefono,
        usuario.correo as correo,
        usuario.genero as genero,
        usuario.nacimiento as nacimiento,
        usuario.fecha_creacion as fecha_creacion,
        medico.especialidad as especialidad
        FROM usuario INNER JOIN medico ON usuario.id = medico.usuario_id LIMIT 100""").fetchall()

    db.close()

    print(medicos)

    return render_template("medico/index.html.j2", medicos=[MedicoFactoryDates(medico) for medico in medicos], session=session)


@app.route("/reportes")
def reportes():
    token = request.cookies.get("auth-cookie")

    session = decode_jwt(token) if token else None

    db = db_injection()

    cursor = db.cursor()

    afectacion = cursor.execute(
        """SELECT COUNT(afectacion), afectacion FROM diagnostico GROUP BY afectacion ORDER BY COUNT(afectacion) DESC LIMIT 1""").fetchall()

    db.close()

    return render_template("reportes/index.html.j2", afectacion=afectacion[0], session=session)


@app.route("/consulta")
def consulta_crear():
    token = request.cookies.get("auth-cookie")

    session = decode_jwt(token) if token else None

    id = request.args.get("id")

    db = db_injection()

    cursor = db.cursor()

    medico_id = cursor.execute(
        f"""SELECT id FROM medico WHERE usuario_id = {id}""").fetchone()

    if not medico_id:
        return render_template("consulta.html.j2", session=session)

    administrativo_id = cursor.execute(
        f"""SELECT id FROM administrativo WHERE medico_id = {medico_id[0]}""").fetchone()

    db.close()

    administrativo_id = administrativo_id[0] if isinstance(
        administrativo_id, tuple) else None

    return render_template("consulta.html.j2", session=session, medico_id=medico_id[0], administrativo_id=administrativo_id, session_info=json.dumps(session))


@app.route("/reporte/medico/<int:medico_ci>")
def reporte_medico(medico_ci: int):
    token = request.cookies.get("auth-cookie")

    session = decode_jwt(token) if token else None

    medico_ci = int(medico_ci)

    db = db_injection()

    cursor = db.cursor()

    medico = cursor.execute(
        """SELECT
        usuario.id as id,
        usuario.nombre as nombre,
        usuario.ci as ci,
        usuario.telefono as telefono,
        usuario.correo as correo,
        usuario.genero as genero,
        usuario.nacimiento as nacimiento,
        usuario.fecha_creacion as fecha_creacion,
        medico.especialidad as especialidad
        FROM usuario INNER JOIN medico ON usuario.id = medico.usuario_id WHERE ci = (?)""", (medico_ci,)).fetchone()

    if not medico:
        db.close()
        return render_template(f"reportes/medico.html.j2", medico_info=None, session=session)

    medico_id = cursor.execute(
        """SELECT
        id
        FROM medico WHERE usuario_id = (?)
        """, (medico[0],)).fetchone()

    administrativo = cursor.execute(
        """SELECT
        usuario.id as id,
        usuario.nombre as nombre,
        usuario.ci as ci,
        usuario.telefono as telefono,
        usuario.correo as correo,
        usuario.genero as genero,
        usuario.nacimiento as nacimiento,
        usuario.fecha_creacion as fecha_creacion,
        administrativo.oficina as oficina,
        administrativo.medico_id as medico_id
        FROM usuario INNER JOIN administrativo ON usuario.id = administrativo.usuario_id WHERE administrativo.medico_id = (?)""", (medico_id[0],)).fetchone()

    consultas = cursor.execute(
        """SELECT
        id,
        fecha_consulta,
        fecha_creacion,
        coste,
        paciente_id,
        medico_id,
        administrativo_id
        FROM consulta
        WHERE medico_id = (?)
        """, (medico_id[0],)).fetchall()

    diagnosticos = []

    if len(consultas) > 0:
        diagnosticos = cursor.execute(
            f"""SELECT
            id,
            afectacion,
            observaciones,
            fecha_creacion,
            consulta_id,
            paciente_id
            FROM diagnostico
            WHERE consulta_id in {str(tuple([el[0] for el in consultas])).rstrip(",)") + ")" if consultas and len(consultas) > 0 else "()"}
            """,
        ).fetchall()

    tratamientos = cursor.execute(
        f"""SELECT
        id,
        indicaciones,
        duracion,
        diagnostico_id
        FROM tratamiento
        WHERE diagnostico_id in {str(tuple([el[0] for el in diagnosticos])).rstrip(",)") + ")" if diagnosticos and len(diagnosticos) > 0 else "()"}
        """,
    ).fetchall()

    administrativo = AdministrativoFactoryDates(
        administrativo) if administrativo else None

    consultas = [ConsultaFactoryDates(consulta) for consulta in consultas]

    diagnosticos = [DiagnosticoFactoryDates(
        diagnostico) for diagnostico in diagnosticos]

    tratamientos = [TratamientoFactoryDates(
        tratamiento) for tratamiento in tratamientos]

    db.close()

    if medico:
        return render_template(f"reportes/medico.html.j2", medico_info=MedicoFactoryDates(medico), administrativo_info=administrativo, consultas=consultas, diagnosticos=diagnosticos, tratamientos=tratamientos,  session=session)

    return render_template(f"reportes/medico.html.j2", medico_info=None, session=session)


@app.route("/reporte/paciente/<int:paciente_ci>")
def reporte_paciente(paciente_ci: int):
    token = request.cookies.get("auth-cookie")

    session = decode_jwt(token) if token else None

    paciente_ci = int(paciente_ci)

    db = db_injection()

    cursor = db.cursor()

    paciente = cursor.execute(
        """SELECT
            usuario.id as id,
            usuario.nombre as nombre,
            usuario.ci as ci,
            usuario.telefono as telefono,
            usuario.correo as correo,
            usuario.genero as genero,
            usuario.nacimiento as nacimiento,
            usuario.fecha_creacion as fecha_creacion,
            paciente.direccion as direccion,
            paciente.religion as religion,
            paciente.sangre as sangre
            FROM usuario INNER JOIN paciente ON usuario.id = paciente.usuario_id WHERE ci = (?)""", (paciente_ci,)).fetchone()

    if not paciente:
        return render_template(f"reportes/paciente.html.j2", paciente_info=None, session=session)

    paciente_id = cursor.execute(
        "SELECT id FROM paciente WHERE usuario_id = (?)", (paciente[0],)).fetchone()

    consultas = cursor.execute(
        """SELECT
        id,
        fecha_consulta,
        fecha_creacion,
        coste,
        paciente_id,
        medico_id,
        administrativo_id
        FROM consulta
        WHERE paciente_id = (?)
        """, (paciente_id[0],)).fetchall()

    diagnosticos = cursor.execute(
        f"""SELECT
        id,
        afectacion,
        observaciones,
        fecha_creacion,
        consulta_id,
        paciente_id
        FROM diagnostico
        WHERE consulta_id in {str(tuple([el[0] for el in consultas])).rstrip(",)") + ")" if consultas and len(consultas) > 0 else "()"}
        """,
    ).fetchall()

    tratamientos = cursor.execute(
        f"""SELECT
        id,
        indicaciones,
        duracion,
        diagnostico_id
        FROM tratamiento
        WHERE diagnostico_id in {str(tuple([el[0] for el in diagnosticos])).rstrip(",)") + ")" if diagnosticos and len(diagnosticos) > 0 else "()"}
        """,
    ).fetchall()

    consultas = [ConsultaFactoryDates(consulta) for consulta in consultas]

    diagnosticos = [DiagnosticoFactoryDates(
        diagnostico) for diagnostico in diagnosticos]

    tratamientos = [TratamientoFactoryDates(
        tratamiento) for tratamiento in tratamientos]

    db.close()

    if paciente:
        return render_template(f"reportes/paciente.html.j2", paciente_info=PacienteFactoryDates(paciente), consultas=consultas, diagnosticos=diagnosticos, tratamientos=tratamientos,  session=session)

    return render_template(f"reportes/paciente.html.j2", medico_info=None, session=session)


@app.route("/reporte/medicos_malos")
def medicos_malos():
    token = request.cookies.get("auth-cookie")

    session = decode_jwt(token) if token else None

    db = db_injection()

    cursor = db.cursor()

    # traemos todas las consultas ordenadas por paciente_id
    consultas = cursor.execute(
        """SELECT
        id,
        fecha_consulta,
        fecha_creacion,
        coste,
        paciente_id,
        medico_id,
        administrativo_id
        FROM consulta
        ORDER BY paciente_id
        """).fetchall()

    # damos forma de diccionario a cada consulta
    consultas = [ConsultaFactoryInt(consulta) for consulta in consultas]

    # variable auxiliar que almacena los ids de las consultas malas
    consultas_malas = []

    if len(consultas) < 2:
        db.close()
        return render_template("reportes/medicos_malos.html.j2", medicos=None)

    # ciclamos hasta la penúltima consulta, pues el paciente de la última consulta claramente no ha vuelta después de la última
    for i in range(len(consultas) - 1):
        consulta = consultas[i]
        consulta_siguiente = consulta_siguiente = consultas[i+1]

        if consulta_siguiente.paciente_id == consulta.paciente_id and abs(consulta_siguiente.fecha_consulta - consulta.fecha_consulta) < 365*24*3600:

            consultas_malas.extend([consulta.id, consulta_siguiente.id])

    if len(consultas_malas) == 0:
        db.close()
        return render_template("reportes/medicos_malos.html.j2", medicos=None)

    diagnosticos = cursor.execute(f"""SELECT
                    afectacion, paciente_id, consulta_id
                    FROM diagnostico WHERE consulta_id in {str(tuple(consultas_malas)).rstrip(",)") + ")" if consultas_malas and len(consultas_malas) > 0 else f"()"} ORDER BY paciente_id""").fetchall()

    if len(diagnosticos) == 0:
        db.close()
        return ApiResponse(error=False, message=["No se encontraron diágnosticos"]).__dict__, 200

    consultas_malas = []

    for i in range(len(diagnosticos) - 1):
        diagnostico_afectacion, diagnostico_paciente_id, consulta_id = diagnosticos[i]
        diagnostico_afectacion_siguiente, diagnostico_paciente_id_siguiente, consulta_id_siguiente = diagnosticos[
            i+1]

        if diagnostico_paciente_id == diagnostico_paciente_id_siguiente and diagnostico_afectacion == diagnostico_afectacion_siguiente:
            consultas_malas.extend(
                [consulta_id, consulta_id_siguiente])

    medicos = cursor.execute(
        f"""SELECT
        usuario.id as id,
        usuario.nombre as nombre,
        usuario.ci as ci,
        usuario.telefono as telefono,
        usuario.correo as correo,
        usuario.genero as genero,
        usuario.nacimiento as nacimiento,
        usuario.fecha_creacion as fecha_creacion,
        medico.especialidad as especialidad
        FROM medico INNER JOIN usuario ON usuario.id = medico.usuario_id
        WHERE medico.id in (SELECT medico_id FROM consulta WHERE id in {str(tuple(consultas_malas)).rstrip(",)") + ")" if consultas_malas and len(consultas_malas) > 0 else "()"})""").fetchall()

    db.close()

    medicos = [MedicoFactoryDates(medico) for medico in medicos]

    print(medicos)

    return render_template("reportes/medicos_malos.html.j2", medicos=medicos, session=session)


@app.route("/reporte/tratamientos")
def tratamientos_efectivos():
    token = request.cookies.get("auth-cookie")

    session = decode_jwt(token) if token else None

    db = db_injection()

    cursor = db.cursor()

    # traemos todas las consultas ordenadas por paciente_id
    consultas = cursor.execute(
        """SELECT
        id,
        fecha_consulta,
        fecha_creacion,
        coste,
        paciente_id,
        medico_id,
        administrativo_id
        FROM consulta
        ORDER BY paciente_id
        """).fetchall()

    # damos forma de diccionario a cada consulta
    consultas = [ConsultaFactoryInt(consulta) for consulta in consultas]

    # variable auxiliar que almacena los ids de las consultas exitosas
    consultas_exitosas = []

    for i in range(len(consultas)):
        consulta = consultas[i]
        consulta_siguiente = None

        # si hay siguiente consulta a la actual la almacenamos
        if i < len(consultas) - 1:
            consulta_siguiente = consultas[i+1]

        # si hay siguiente consulta a la actual Y ambas consultas son del mismo paciente chequeamos si la diferencia de las fechas de consulta
        # es mayor a un año
        if consulta_siguiente and consulta_siguiente.paciente_id == consulta.paciente_id:

            if (abs(consulta_siguiente.fecha_consulta - consulta.fecha_consulta) > 365*24*3600):
                consultas_exitosas.append(consulta.id)

            # si no hay siguiente consulta del mismo paciente, entonces revisamos si la fecha de esa consulta es de hace un año o más
        elif consulta.fecha_consulta < (get_unix_now() - 365*24*3600):
            consultas_exitosas.append(consulta.id)

    if len(consultas_exitosas) == 0:
        db.close()
        return render_template("reportes/tratamientos_efectivos.html.j2", tratamientos=None)

    diagnosticos = cursor.execute(f"""SELECT
                    id
                    FROM diagnostico WHERE consulta_id in {str(tuple(consultas_exitosas)).rstrip(",)") + ")" if len(consultas_exitosas) > 0 else "()"}""").fetchall()

    if len(diagnosticos) == 0:
        db.close()
        return ApiResponse(error=False, message=["No se encontraron diágnosticos"]).__dict__, 200

    tratamientos = cursor.execute(
        f"""SELECT id, indicaciones, duracion, diagnostico_id FROM tratamiento WHERE diagnostico_id in {tuple([diagnostico[0] for diagnostico in diagnosticos])}""").fetchall()

    tratamientos = [TratamientoFactoryDates(
        tratamiento) for tratamiento in tratamientos]

    db.close()

    return render_template("reportes/tratamientos_efectivos.html.j2", tratamientos=tratamientos, session=session)


@app.route("/reporte/especialidades")
def especialidades():
    token = request.cookies.get("auth-cookie")

    session = decode_jwt(token) if token else None

    db = db_injection()

    cursor = db.cursor()

    especialidades = cursor.execute(
        """SELECT COUNT(consulta.paciente_id), medico.especialidad FROM consulta INNER JOIN medico ON medico.id = consulta.medico_id GROUP BY medico.especialidad ORDER BY COUNT(consulta.paciente_id) DESC""").fetchall()

    db.close()

    esp = []

    for i in range(len(especialidades)):
        esp.append(
            f"{i+1}. {especialidades[i][1]} con {especialidades[i][0]} consultas")

    return render_template("reportes/especialidades.html.j2", especialidades=esp, session=session)


@app.route("/actualizar")
def actualizar():
    token = request.cookies.get("auth-cookie")

    session = decode_jwt(token) if token else None

    if not session:
        return redirect("/login")

    return render_template("/actualizar.html.j2", session=session, session_info=json.dumps(session))


@app.post("/api/login")
def login_request():
    try:
        body = request.get_json()

        if not body.get("correo") or not body.get("clave"):
            raise ParsingException(["La información no es válida"])

        db = db_injection()

        cursor = db.cursor()

        usuario = cursor.execute(
            """SELECT
            id,
            nombre,
            clave,
            ci,
            telefono,
            correo,
            genero,
            nacimiento,
            fecha_creacion
            FROM usuario WHERE correo = (?)""", (body.get("correo"),)).fetchone()

        if not usuario:
            raise ParsingException(["No se encontró el usuario"])

        if usuario[2] != body.get("clave"):
            raise ParsingException(["La clave no es válida"])

        paciente = cursor.execute(
            """SELECT
            direccion,
            religion,
            sangre
            FROM paciente WHERE usuario_id = (?)""", (usuario[0],)).fetchone()

        medico = cursor.execute(
            """SELECT
            especialidad
            FROM medico WHERE usuario_id = (?)""", (usuario[0],)).fetchone()

        administrativo = cursor.execute(
            """SELECT
            oficina,
            medico_id
            FROM administrativo WHERE usuario_id = (?)""", (usuario[0],)).fetchone()

        db.close()

        if paciente:
            usuario = list(usuario)
            usuario.pop(2)
            usuario.extend(list(paciente))
            if usuario == None:
                raise ParsingException(["Error con el usuario"])
            usuario = PacienteFactoryDates(usuario)
        elif medico:
            usuario = list(usuario)
            usuario.pop(2)
            usuario.extend(list(medico))
            if usuario == None:
                raise ParsingException(["Error con el usuario"])
            usuario = MedicoFactoryDates(usuario)
        elif administrativo:
            usuario = list(usuario)
            usuario.pop(2)
            usuario.extend(list(administrativo))
            if usuario == None:
                raise ParsingException(["Error con el usuario"])
            usuario = AdministrativoFactoryDates(usuario)
        else:
            db.close()
            raise ParsingException(
                ["No se encontró información referente al usuario"])

        res = make_response(ApiResponsePayload(error=False, message=[
                            "Inicio de sesión exitoso"], payload=usuario).__dict__)

        token = encode_jwt(usuario)

        res.set_cookie("auth-cookie", token, path="/", httponly=True)

        return res
    except Exception as err:
        return ApiErrorHandler(err, defaultMessage="Ocurrió un error con el login").__dict__, 400


@app.delete("/api/logout")
def logout():
    try:
        res = make_response(ApiResponse(error=False, message=[
                            "Cerrando sesión..."]).__dict__)

        res.delete_cookie("auth-cookie")

        return res
    except Exception as err:
        return ApiErrorHandler(err, "No se encontró sesión activa").__dict__, 400


@app.route("/signup")
def signup():
    token = request.cookies.get("auth-cookie")

    session = decode_jwt(token) if token else None

    if session:
        return redirect("/")

    return render_template("signup.html.j2")


@app.get("/api/setup")
def setup():
    try:
        p = request.args.get("p")

        if not p or p != config.get("SETUP_PASSWORD"):
            return ApiResponse(error=True, message=["Clave inválida"]).__dict__, 400

        setUpDatabase()

        return ApiResponse(error=False, message=["Base de datos iniciada"]).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, "Ocurrió un error iniciando la DB").__dict__, 400


@app.errorhandler(404)
def not_found(e):
    token = request.cookies.get("auth-cookie")

    session = decode_jwt(token) if token else None

    return render_template("404.html.j2", session=session)


if __name__ == "__main__":
    app.run(port=5000)
