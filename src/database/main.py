import sqlite3


def db_injection():
    return sqlite3.connect(
        database="./src/database/compu.db"
    )


def setUpDatabase():
    conn = db_injection()

    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS usuario (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        ci INTEGER NOT NULL,
                        telefono TEXT NOT NULL,
                        correo TEXT NOT NULL,
                        genero CHAR,  
                        nacimiento INTEGER NOT NULL,
                        fecha_creacion INT NOT NULL,

                        UNIQUE(ci)
                        )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS paciente (
                        id INTEGER PRIMARY KEY,
                        direccion TEXT NOT NULL,
                        religion TEXT,
                        sangre TEXT NOT NULL,
                        usuario_id INTEGER NOT NULL,
                    
                        FOREIGN KEY(usuario_id) REFERENCES usuario(id)
                        )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS administrativo (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        oficina TEXT NOT NULL,
                        medico_id INTEGER NOT NULL,
                        usuario_id INTEGER NOT NULL,
                    
                        FOREIGN KEY(medico_id) REFERENCES medico(id),
                        FOREIGN KEY(usuario_id) REFERENCES usuario(id)
                        )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS consulta (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha_consulta INTEGER NOT NULL,
                        fecha_creacion INTEGER NOT NULL,
                        coste REAL NOT NULL,
                        paciente_id INTEGER NOT NULL,
                        medico_id INTEGER NOT NULL,
                        administrativo_id INTEGER NOT NULL,
                   
                        FOREIGN KEY(paciente_id) REFERENCES paciente(id),
                        FOREIGN KEY(medico_id) REFERENCES medico(id),
                        FOREIGN KEY(administrativo_id) REFERENCES administrativo(id)
                        )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS medico (
                        id INTEGER PRIMARY KEY,
                        especialidad TEXT NOT NULL,
                        usuario_id INTEGER NOT NULL,

                        FOREIGN KEY(usuario_id) REFERENCES usuario(id)
                        )""")

    # cursor.execute("DROP TABLE IF EXISTS diagnostico")

    cursor.execute("""CREATE TABLE IF NOT EXISTS diagnostico (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        afectacion TEXT NOT NULL,
                        observaciones TEXT NOT NULL,
                        fecha_creacion INTEGER NOT NULL,
                        paciente_id INTEGER NOT NULL,
                        consulta_id INTEGER NOT NULL,
                    
                        FOREIGN KEY(consulta_id) REFERENCES consulta(id),
                        FOREIGN KEY(paciente_id) REFERENCES paciente(id)
                        )""")

    # cursor.execute("DROP TABLE IF EXISTS tratamiento")

    cursor.execute("""CREATE TABLE IF NOT EXISTS tratamiento (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        indicaciones TEXT NOT NULL,
                        duracion INTEGER,
                        diagnostico_id INTEGER NOT NULL,

                        FOREIGN KEY(diagnostico_id) REFERENCES dianostico(id)
                        )""")

    # cursor.execute("DROP TABLE IF EXISTS contacto")

    cursor.execute("""CREATE TABLE IF NOT EXISTS contacto (
                        id INTEGER PRIMARY KEY,
                        nombre TEXT NOT NULL,
                        ci INTEGER NOT NULL,
                        correo TEXT NOT NULL,
                        relacion TEXT NOT NULL,
                        telefono TEXT NOT NULL,
                        genero TEXT NOT NULL,
                        nacimiento INTEGER NOT NULL,
                   
                        UNIQUE(ci)
                        )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS contacto_en_paciente (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        paciente_id INTEGER NOT NULL,
                        contacto_id INTEGER NOT NULL,

                        FOREIGN KEY(paciente_id) REFERENCES paciente(id),
                        FOREIGN KEY(contacto_id) REFERENCES contacto(id)
                        )""")

    conn.close()
