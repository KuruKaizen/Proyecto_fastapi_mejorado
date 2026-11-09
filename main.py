# ============================================
# API REST - CONSULTA DE ESTUDIANTES IUTIRLA
# Estudiante: Angel Vasquez
# Cédula: V-32439699
# ============================================

from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from modelos import Estudiante, EstudianteCreate, EstudianteNotasCreate
from datos import estudiantes_db, buscar_estudiante, filtrar_por_seccion, obtener_aprobados

# Crear la aplicación FastAPI
app = FastAPI(
    title="Sistema de Estudiantes IUTIRLA",
    description="API para consultar estudiantes de Programación III",
    version="1.0.0",
    contact={"name": "Prof. Jhonatan Fernandez"}
)

# ============================================
# ENDPOINTS (RUTAS DE LA API)
# ============================================

@app.get("/")
def raiz():
    """Endpoint raíz - Información general"""
    return {
        "mensaje": "Bienvenido a la API de Estudiantes IUTIRLA",
        "profesor": "Jhonatan Fernandez",
        "asignatura": "Programación III",
        "documentacion": "/docs"
    }

@app.get("/estudiantes", summary="Consultar Estudiantes")
def listar_estudiantes(
    seccion: Optional[str] = Query(None, description="Filtrar por sección"),
    cedula: Optional[str] = Query(None, description="Filtrar por cédula")
):
    """
    REQUERIMIENTO 2: Consultar estudiantes.
    Permite filtrar opcionalmente por sección o cédula en la URL, 
    calculando el promedio y determinando el estatus de cada estudiante.
    """
    resultado = estudiantes_db
    
    # Filtrar si el usuario envió parámetros en la URL
    if seccion:
        resultado = [est for est in resultado if est.seccion == seccion]
    if cedula:
        resultado = [est for est in resultado if est.cedula == cedula]

    # Recalcular promedio y estatus al momento de generar la respuesta
    lista_salida = []
    for est in resultado:
        lista_salida.append({
            "cedula": est.cedula,
            "nombre": est.nombre,
            "apellido": est.apellido,
            "seccion": est.seccion,
            "nota": est.nota,
            "activo": est.activo,
            "promedio": est.nota,
            "estatus": est.get_estatus()
        })
    return lista_salida

@app.get("/estudiantes/{cedula}", response_model=Estudiante)
def obtener_estudiante(cedula: str):
    """Obtener un estudiante específico por cédula"""
    estudiante = buscar_estudiante(cedula)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return estudiante

@app.get("/estudiantes/seccion/{seccion}", response_model=List[Estudiante])
def estudiantes_por_seccion(seccion: str):
    """Obtener todos los estudiantes de una sección específica"""
    resultado = filtrar_por_seccion(seccion)
    if not resultado:
        raise HTTPException(status_code=404, detail=f"No hay estudiantes en la sección {seccion}")
    return resultado

@app.get("/estadisticas")
def obtener_estadisticas():
    """Obtener estadísticas generales del sistema"""
    total = len(estudiantes_db)
    aprobados = len(obtener_aprobados())
    reprobados = total - aprobados
    promedio = sum(est.nota for est in estudiantes_db) / total if total > 0 else 0

    return {
        "total_estudiantes": total,
        "aprobados": aprobados,
        "reprobados": reprobados,
        "promedio_general": round(promedio, 2),
        "porcentaje_aprobacion": round((aprobados/total)*100, 2) if total > 0 else 0
    }

@app.post("/estudiantes", response_model=Estudiante, status_code=201)
def crear_estudiante(estudiante: EstudianteCreate):
    """Registrar un nuevo estudiante"""
    if buscar_estudiante(estudiante.cedula):
        raise HTTPException(status_code=400, detail="La cédula ya está registrada")

    nuevo = Estudiante(**estudiante.dict(), activo=True)
    estudiantes_db.append(nuevo)
    return nuevo

@app.post("/estudiantes/{cedula}/notas", status_code=200)
def cargar_actualizar_notas(cedula: str, datos: EstudianteNotasCreate):
    """Requerimiento 1: Cargar o actualizar notas mediante POST (exactamente 1 método POST aquí)"""
    if datos.cedula != cedula:
        raise HTTPException(status_code=400, detail="La cédula de la ruta y del cuerpo no coinciden")

    # Calcular promedio de las 5 notas
    promedio = sum(datos.notas) / len(datos.notas)

    # Buscar si la cédula ya existe
    estudiante_existente = buscar_estudiante(cedula)

    if estudiante_existente:
        estudiante_existente.nombre = datos.nombre
        estudiante_existente.apellido = datos.apellido
        estudiante_existente.seccion = datos.seccion
        estudiante_existente.nota = round(promedio, 2)
        estudiante = estudiante_existente
        mensaje = "Notas actualizadas exitosamente"
    else:
        nuevo_est = Estudiante(
            cedula=cedula,
            nombre=datos.nombre,
            apellido=datos.apellido,
            seccion=datos.seccion,
            nota=round(promedio, 2),
            activo=True
        )
        estudiantes_db.append(nuevo_est)
        estudiante = nuevo_est
        mensaje = "Estudiante creado y notas cargadas exitosamente"

    return {
        "mensaje": mensaje,
        "estudiante": {
            "cedula": estudiante.cedula,
            "nombre": estudiante.nombre,
            "apellido": estudiante.apellido,
            "seccion": estudiante.seccion,
            "activo": estudiante.activo
        },
        "promedio_calculado": round(promedio, 2),
        "estatus": estudiante.get_estatus()
    }

@app.delete("/estudiantes/{cedula}", response_model=dict)
def eliminar_estudiante(cedula: str):
    """Eliminar un estudiante por su cédula"""
    estudiante = buscar_estudiante(cedula)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    estudiantes_db.remove(estudiante)
    return {
        "mensaje": "Estudiante eliminado exitosamente",
        "cedula": cedula
    }

# ============================================
# PUNTO DE ENTRADA
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)