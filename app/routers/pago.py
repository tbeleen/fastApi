from fastapi import APIRouter, HTTPException
from typing import Optional
from app.database import get_conexion
from datetime import datetime

router = APIRouter(
    prefix="/pagos",
    tags=["Pagos"]
)

# -------------------- POST NUEVO PAGO --------------------
@router.post("/")
def registrar_pago(rut_usuario: str, id_tipo_pago: int, monto: float):
    try:
        if monto <= 0:
            raise HTTPException(status_code=400, detail="El monto debe ser mayor a cero")
        if id_tipo_pago not in [1, 2, 3]:
            raise HTTPException(status_code=400, detail="ID de tipo de pago inválido")

        cone = get_conexion()
        cursor = cone.cursor()

        # Verificar si el rut del usuario existe
        cursor.execute("SELECT 1 FROM usuario WHERE rut = :rut", {"rut": rut_usuario})
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Verificar si el tipo de pago existe
        cursor.execute("SELECT 1 FROM tipo_pago WHERE id_tipo_pago = :id", {"id": id_tipo_pago})
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Tipo de pago no válido")

        # Insertar el pago
        cursor.execute("""
            INSERT INTO pago (rut_usuario, id_tipo_pago, monto)
            VALUES (:rut_usuario, :id_tipo_pago, :monto)
        """, {
            "rut_usuario": rut_usuario,
            "id_tipo_pago": id_tipo_pago,
            "monto": monto
        })
        cone.commit()
        cursor.close()
        cone.close()
        return {"mensaje": "Pago registrado con éxito"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


# -------------------- GET TODOS LOS PAGOS --------------------
@router.get("/")
def obtener_pagos():
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("""
            SELECT DISTINCT p.id_pago, p.rut_usuario, u.nombre, u.apellido, p.id_tipo_pago, tp.descripcion, p.monto, p.fecha_pago
            FROM pago p
            JOIN usuario u ON p.rut_usuario = u.rut
            JOIN tipo_pago tp ON p.id_tipo_pago = tp.id_tipo_pago
            ORDER BY p.fecha_pago DESC
        """)
        pagos = []
        for fila in cursor:
            pagos.append({
                "rut_usuario": fila[1],
                "nombre": fila[2],
                "apellido": fila[3],
                "id_tipo_pago": fila[4],
                "tipo_pago": fila[5],
                "monto": fila[6],
                "fecha_pago": fila[7].strftime("%Y-%m-%d %H:%M:%S")
            })
        cursor.close()
        cone.close()
        return pagos
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


# -------------------- GET PAGOS POR RUT --------------------
@router.get("/{rut}")
def obtener_pagos_por_usuario(rut: str):
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("""
            SELECT p.id_pago, p.id_tipo_pago, tp.descripcion, p.monto, p.fecha_pago
            FROM pago p
            JOIN tipo_pago tp ON p.id_tipo_pago = tp.id_tipo_pago
            WHERE p.rut_usuario = :rut
            ORDER BY p.fecha_pago DESC
        """, {"rut": rut})
        pagos = cursor.fetchall()
        cursor.close()
        cone.close()

        if not pagos:
            raise HTTPException(status_code=404, detail="No se encontraron pagos para este usuario")

        return [
            {
                "id_pago": pago[0],
                "id_tipo_pago": pago[1],
                "tipo_pago": pago[2],
                "monto": pago[3],
                "fecha_pago": pago[4].strftime("%Y-%m-%d %H:%M:%S")
            } for pago in pagos
        ]
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


# -------------------- DELETE PAGO POR ID --------------------
@router.delete("/{id_pago}")
def eliminar_pago(id_pago: int):
    try:
        cone = get_conexion()
        cursor = cone.cursor()
        cursor.execute("DELETE FROM pago WHERE id_pago = :id", {"id": id_pago})
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        cone.commit()
        cursor.close()
        cone.close()
        return {"mensaje": "Pago eliminado con éxito"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
