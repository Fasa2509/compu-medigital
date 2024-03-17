from flask import Blueprint

from src.custom_types.medico import MedicoFactory
from src.helpers.dates import get_unix_now
from src.custom_types.tratamiento import TratamientoFactory
from src.custom_types.diagnostico import DiagnosticoFactory
from src.custom_types.consulta import ConsultaFactory, ConsultaFactoryInt
from src.custom_types.administrativo import AdministrativoFactory
from src.database.main import db_injection
from src.custom_types.Api import ApiResponse, ApiResponsePayload
from src.errors.main import ApiErrorHandler, DbException


bp = Blueprint("reportes", __name__, template_folder="templates")


@bp.get("/medico/<int:medico_ci>")
def obtener_historial_medico(medico_ci: int):
    try:
        medico_ci = int(medico_ci)

        db = db_injection()

        cursor = db.cursor()

        medico_id = cursor.execute(
            "SELECT id FROM medico WHERE usuario_id = (SELECT id FROM usuario WHERE ci = ?)", (medico_ci,)).fetchone()

        if not medico_id:
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
            FROM usuario INNER JOIN administrativo ON usuario.id = administrativo.usuario_id WHERE medico_id = (?)""", (medico_id[0],)).fetchone()

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

        consultas = [ConsultaFactory(consulta) for consulta in consultas]

        diagnosticos = [DiagnosticoFactory(
            diagnostico) for diagnostico in diagnosticos]

        tratamientos = [TratamientoFactory(
            tratamiento) for tratamiento in tratamientos]

        db.close()

        return ApiResponsePayload(error=False, message=["Reporte obtenido"], payload={"administrativo": AdministrativoFactory(administrativo), "consultas": consultas, "diagnosticos": diagnosticos, "tratamientos": tratamientos}).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, defaultMessage="Ocurrió un error generando el historial").__dict__, 400


@bp.get("/paciente/<int:paciente_ci>")
def obtener_historial_paciente(paciente_ci: int):
    try:
        paciente_ci = int(paciente_ci)

        db = db_injection()

        cursor = db.cursor()

        paciente_id = cursor.execute(
            "SELECT id FROM paciente WHERE usuario_id = (SELECT id FROM usuario WHERE ci = ?)", (paciente_ci,)).fetchone()

        if not paciente_id:
            raise DbException(["No se encontró el paciente"])

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
            WHERE consulta_id in {tuple([el[0] for el in consultas]) if len(consultas) > 1 else f"({consultas[0][0]})"}
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

        consultas = [ConsultaFactory(consulta) for consulta in consultas]

        diagnosticos = [DiagnosticoFactory(
            diagnostico) for diagnostico in diagnosticos]

        tratamientos = [TratamientoFactory(
            tratamiento) for tratamiento in tratamientos]

        db.close()

        return ApiResponsePayload(error=False, message=["Reporte obtenido"], payload={"consultas": consultas, "diagnosticos": diagnosticos, "tratamientos": tratamientos}).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, defaultMessage="Ocurrió un error generando el historial").__dict__, 400


@bp.get("/especialidades")
def obtener_reporte_especialidades():
    try:
        db = db_injection()

        cursor = db.cursor()

        especialidades = cursor.execute(
            """SELECT COUNT(consulta.paciente_id), medico.especialidad FROM consulta INNER JOIN medico ON medico.id = consulta.medico_id GROUP BY medico.especialidad ORDER BY COUNT(consulta.paciente_id) DESC""").fetchall()

        db.close()

        return ApiResponsePayload(error=False, message=["Reporte obtenido"], payload={"data": especialidades}).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, defaultMessage="Ocurrió un error generando el reporte").__dict__, 400


@bp.get("/medicos")
def obtener_medicos_malos():
    try:
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
            return ApiResponse(error=False, message=["No hay suficientes consultas"]).__dict__

        # ciclamos hasta la penúltima consulta, pues el paciente de la última consulta claramente no ha vuelta después de la última
        for i in range(len(consultas) - 1):
            consulta = consultas[i]
            consulta_siguiente = consulta_siguiente = consultas[i+1]

            if consulta_siguiente.paciente_id == consulta.paciente_id and abs(consulta_siguiente.fecha_consulta - consulta.fecha_consulta) < 365*24*3600:

                consultas_malas.extend([consulta.id, consulta_siguiente.id])

        if len(consultas_malas) == 0:
            db.close()
            return ApiResponse(error=False, message=["No se encontraron consultas malas"]).__dict__, 200

        diagnosticos = cursor.execute(f"""SELECT
                        afectacion, paciente_id, consulta_id
                        FROM diagnostico WHERE consulta_id in {tuple(consultas_malas) if len(consultas_malas) > 1 else f"({consultas_malas[0]})"} ORDER BY paciente_id""").fetchall()

        if len(diagnosticos) == 0:
            db.close()
            return ApiResponse(error=False, message=["No se encontraron diágnosticos"]).__dict__, 200

        print(diagnosticos)
        print([diagnostico[0] for diagnostico in diagnosticos])

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
            WHERE medico.id in (SELECT medico_id FROM consulta WHERE id in {tuple(consultas_malas)})""").fetchall()

        db.close()

        medicos = [MedicoFactory(medico) for medico in medicos]

        return ApiResponsePayload(error=False, message=["Reporte médico obtenido"], payload={"data": medicos}).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, defaultMessage="Ocurrió un error generando el report de médicos").__dict__, 400


@bp.get("/tratamientos")
def obtener_reporte_tratamientos():
    try:
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

            # print(consulta)

            # si hay siguiente consulta a la actual Y ambas consultas son del mismo paciente chequeamos si la diferencia de las fechas de consulta
            # es mayor a un año
            if consulta_siguiente and consulta_siguiente.paciente_id == consulta.paciente_id:
                # print(consulta_siguiente)
                # print(get_datetime_from_unix(consulta.fecha_consulta))
                # print(get_datetime_from_unix(
                #     consulta_siguiente.fecha_consulta), end="\n\n")

                # print(abs(consulta_siguiente.fecha_consulta -
                #       consulta.fecha_consulta) > 365*24*3600)

                if (abs(consulta_siguiente.fecha_consulta - consulta.fecha_consulta) > 365*24*3600):
                    consultas_exitosas.append(consulta.id)

                # si no hay siguiente consulta del mismo paciente, entonces revisamos si la fecha de esa consulta es de hace un año o más
            else:
                # print(get_datetime_from_unix(consulta.fecha_consulta))
                # print(consulta.fecha_consulta < (get_unix_now() - 365*24*3600))

                if consulta.fecha_consulta < (get_unix_now() - 365*24*3600):
                    consultas_exitosas.append(consulta.id)
            # print()

        if len(consultas_exitosas) == 0:
            db.close()
            return ApiResponse(error=False, message=["No se encontraron consultas exitosas"]).__dict__, 200

        diagnosticos = cursor.execute(f"""SELECT
                        id
                        FROM diagnostico WHERE consulta_id in {tuple(consultas_exitosas) if len(consultas_exitosas) > 1 else f"({consultas_exitosas[0]})"}""").fetchall()

        if len(diagnosticos) == 0:
            db.close()
            return ApiResponse(error=False, message=["No se encontraron diágnosticos"]).__dict__, 200

        tratamientos = cursor.execute(
            f"""SELECT id, indicaciones, duracion, diagnostico_id FROM tratamiento WHERE diagnostico_id in {tuple([diagnostico[0] for diagnostico in diagnosticos])}""").fetchall()

        tratamientos = [TratamientoFactory(
            tratamiento) for tratamiento in tratamientos]

        db.close()

        return ApiResponsePayload(error=False, message=["Reporte obtenido"], payload={"data": tratamientos}).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, defaultMessage="Ocurrió un error generando el reporte").__dict__, 400


@bp.get("/diagnostico")
def obtener_reporte_diagnosticos():
    try:
        db = db_injection()

        cursor = db.cursor()

        afectacion = cursor.execute(
            """SELECT COUNT(afectacion), afectacion FROM diagnostico GROUP BY afectacion ORDER BY COUNT(afectacion) DESC LIMIT 1""").fetchall()

        db.close()

        return ApiResponsePayload(error=False, message=["Reporte obtenido"], payload={"data": afectacion}).__dict__, 200
    except Exception as err:
        return ApiErrorHandler(err, defaultMessage="Ocurrió un error generando el reporte").__dict__, 400
