import oracledb 
from fastapi import HTTPException
def get_conexion():
    try:
        conexion = oracledb.connect(
            user="api_sitioferremas",
            password="api_sitioferremas",
            dsn="localhost:1521/XE"
        )
        return conexion
    except oracledb.DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar a la base de datos: {e}")