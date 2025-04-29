import oracledb

def get_conexion():
    conexion = oracledb.connect(
        user="ejemplo_fastapi",
        password="ejemplo_fastapi",
        dsn="localhost:1521/orcl.duoc.com.cl"
    )
    return conexion

