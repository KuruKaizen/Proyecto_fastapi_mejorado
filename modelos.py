# ============================================
# MODELOS DE DATOS - FASTAPI + PYDANTIC
# Estudiante: Angel Vasquez
# Cédula: V-32439699
# ============================================

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class Estudiante(BaseModel):
    """Modelo que representa un estudiante del IUTIRLA"""
    cedula: str = Field(..., description="Cédula de identidad")
    nombre: str = Field(..., description="Nombre del estudiante")
    apellido: str = Field(..., description="Apellido del estudiante")
    seccion: str = Field(..., description="Sección académica")
    nota: float = Field(..., ge=0, le=20, description="Nota final (0-20)")
    activo: bool = Field(default=True, description="¿Está activo?")

    # Método para verificar si aprobó
    def aprobo(self) -> bool:
        return self.nota >= 10

    # Método para obtener estatus
    def get_estatus(self) -> str:
        if self.nota >= 18:
            return "EXCELENTE"
        elif self.nota >= 14:
            return "BUENO"
        elif self.nota >= 10:
            return "SATISFACTORIO"
        else:
            return "DEFICIENTE"

class EstudianteCreate(BaseModel):
    """Modelo para crear nuevo estudiante (sin cédula automática)"""
    cedula: str
    nombre: str
    apellido: str
    seccion: str
    nota: float

class EstudianteNotasCreate(BaseModel):
    """Modelo para el Requerimiento 1: Cargar o actualizar notas con 5 notas exactas"""
    cedula: str
    nombre: str
    apellido: str
    seccion: str
    notas: List[float] = Field(..., description="Lista de exactamente 5 notas")

    @field_validator('notas')
    @classmethod
    def validar_notas(cls, v):
        if len(v) != 5:
            raise ValueError("La lista debe contener exactamente 5 notas.")
        for nota in v:
            if not (0 <= nota <= 20):
                raise ValueError("Cada nota debe ser un número entre 0 y 20.")
        return v