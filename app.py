from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv, dotenv_values
from flask_cors import CORS
from src.errors.main import ApiErrorHandler

from src.database.main import db_injection, setUpDatabase
from src.custom_types.Api import ApiResponse
from src.routes import usuario, paciente, medico, administrativo, consulta, diagnostico, tratamiento, contacto, reporte

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
administrativo_api = app.register_blueprint(administrativo.bp, url_prefix='/api/administrativo')

# registramos blueprint API de consultas
consulta_api = app.register_blueprint(consulta.bp, url_prefix='/api/consulta')

# registramos blueprint API de diagnosticos
diagnostico_api = app.register_blueprint(diagnostico.bp, url_prefix='/api/diagnostico')

# registramos blueprint API de tratamientos
tratamiento_api = app.register_blueprint(tratamiento.bp, url_prefix='/api/tratamiento')

# registramos blueprint API de tratamientos
contacto_api = app.register_blueprint(contacto.bp, url_prefix='/api/contacto')

# registramos blueprint API de historiales
historial_api = app.register_blueprint(reporte.bp, url_prefix='/api/reporte')


@app.route('/')
def index():
    conn = db_injection()

    cursor = conn.cursor()

    usuarios = cursor.execute("SELECT * FROM usuario").fetchall()

    print(usuarios)

    conn.close()

    return render_template("index.html.j2", usuarios=usuarios)


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
