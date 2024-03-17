from flask import Blueprint, request

from src.custom_types.consulta import ConsultaFactoryDates
from src.custom_types.diagnostico import DiagnosticoFactoryDates
from src.custom_types.tratamiento import TratamientoFactory
from src.database.main import db_injection
from src.custom_types.usuario import ActualizarUsuario, NuevoUsuario
from src.custom_types.Api import ApiResponse, ApiResponsePayload
from src.custom_types.medico import ActualizarMedico, MedicoFactory, NuevoMedico
from src.errors.main import ApiErrorHandler, DbException


bp = Blueprint("medicos", __name__, template_folder="templates")


@bp.get("/<int:medico_ci>")
def obtener_medico(medico_ci: int):
    try:
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
            raise DbException(["No se encontró el médico"])

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
            FROM usuario INNER JOIN administrativo ON usuario.id = administrativo.usuario_id WHERE medico_id = (?)""", (medico[0],)).fetchone()

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
            """, (medico[0],)).fetchall()

        diagnosticos = cursor.execute(
            f"""SELECT
            id,
            afectacion,
            observaciones,
            fecha_creacion,
            consulta_id,
            paciente_id
            FROM diagnostico
            WHERE consulta_id in {tuple([el[0] for el in consultas])}
            """,
        ).fetchall()

        tratamientos = cursor.execute(
            f"""SELECT
            id,
            indicaciones,
            duracion,
            diagnostico_id
            FROM tratamiento
            WHERE diagnostico_id in {tuple([el[0] for el in diagnosticos])}
            """,
        ).fetchall()

        consultas = [ConsultaFactoryDates(consulta) for consulta in consultas]

        diagnosticos = [DiagnosticoFactoryDates(
            diagnostico) for diagnostico in diagnosticos]

        tratamientos = [TratamientoFactory(
            tratamiento) for tratamiento in tratamientos]

        db.close()

        return ApiResponsePayload(error=False, message=["El médico fue obtenido"], payload={"medico": MedicoFactory(medico)}).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, "Ocurrió un error obteniendo el médico").__dict__, 400


@bp.post("/")
def crear_medico():
    try:
        usuario = NuevoUsuario(**request.get_json())
        medico = NuevoMedico(**request.get_json())

        if not usuario.clave or len(usuario.clave) < 8:
            raise ValueError("La contraseña no es válida")

        db = db_injection()

        cursor = db.cursor()

        cursor.execute("INSERT INTO usuario (nombre, clave, ci, telefono, correo, genero, nacimiento, fecha_creacion) VALUES (:nombre, :clave, :ci, :telefono, :correo, :genero, :nacimiento, :fecha_creacion)",
                       usuario.__dict__)

        usuario_id = cursor.lastrowid

        medico = {**medico.__dict__, "usuario_id": usuario_id}

        cursor.execute("INSERT INTO medico (especialidad, usuario_id) VALUES (:especialidad, :usuario_id)",
                       medico)

        db.commit()

        return ApiResponsePayload(error=False, message=["El medico fue creado"], payload={"id": usuario_id, **usuario.__dict__}).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, "Ocurrió un error creando el medico").__dict__, 400


@bp.put("/")
def actualizar_paciente():
    try:
        usuario_info = ActualizarUsuario(**request.get_json())
        medico_info = ActualizarMedico(**request.get_json())
        medico_id = medico_info.id

        db = db_injection()

        medico_info = request.get_json()

        cursor = db.cursor()

        cursor.execute(f"""UPDATE medico SET
                        especialidad = :especialidad
                        WHERE id = {medico_id}""", medico_info)

        cursor.execute(f"""UPDATE usuario SET
                        nombre = :nombre,
                        ci = :ci,
                        telefono = :telefono
                        WHERE id = (SELECT usuario_id FROM medico WHERE id = {medico_id})""", usuario_info.__dict__)

        db.commit()

        db.close()

        return ApiResponse(error=False, message=["El medico fue actualizado"]).__dict__, 200
    except Exception as err:
        print(err)
        return ApiResponse(error=True, message=["Ocurrió un error actualizando el medico"]).__dict__, 400


@bp.delete("/<int:medico_id>")
def eliminar_paciente(medico_id: int):
    try:
        medico_id = int(medico_id)

        db = db_injection()

        cursor = db.cursor()

        cursor.execute(
            f"DELETE FROM usuario WHERE id = (SELECT usuario_id FROM medico WHERE id = ?)", (medico_id,))

        db.commit()

        cursor.execute(f"DELETE FROM medico WHERE id = (?)", (medico_id,))

        db.commit()

        db.close()

        return ApiResponse(error=False, message=["El medico fue eliminado"]).__dict__, 200
    except Exception as err:
        print(err)
        return ApiResponse(error=True, message=["Ocurrió un error eliminando el medico"]).__dict__, 400
