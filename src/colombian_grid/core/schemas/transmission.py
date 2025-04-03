from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SubstationEntity(BaseModel):
    elementName: str = Field(..., title="Nombre de la subestación")
    fpoDate: Optional[datetime | str] = Field(
        ...,
        title="Fecha de puesta en operación",
        description="Formato: YYYY-MM-DDTHH:MM:SS",
    )
    voltage: Optional[str] = Field(
        ..., title="Voltajes", description="Voltajes de la subestación"
    )
    latitude: Optional[float] = Field(..., title="Latitud")
    longitude: Optional[float] = Field(..., title="Longitud")
    operatorCompanyName: Optional[str] = Field(
        ..., title="Nombre de la empresa operadora"
    )
    subArea: Optional[str] = Field(..., title="Subárea")
    department: Optional[str] = Field(..., title="Departamento")
    elementId: Optional[int] = Field(..., title="ID de la subestación")
    substationVoltageLevelId: Optional[int] = Field(
        ..., title="ID del nivel de voltaje de la subestación"
    )
    subAreaId: Optional[int] = Field(..., title="ID de la subárea")
    voltagesList: list[str] = Field(
        ...,
        title="Lista de voltajes",
        description="Lista de voltajes de la subestación",
    )


class TransmissionLineProperties(BaseModel):
    nameLine: str = Field(..., title="Nombre de la línea")
    color: str = Field(..., title="Color de la línea")
    energy: str = Field(..., title="Voltaje de la línea")
    sub1: str = Field(..., title="Subestación 1")
    sub2: str = Field(..., title="Subestación 2")
    operator: str = Field(..., title="Operador")
    longitude: float = Field(..., title="Longitud")
    emergencyLimit: float = Field(..., title="Límite de emergencia")
    ratedCurrent: float = Field(..., title="Corriente nominal")
    subArea1: int = Field(..., title="ID de la subárea 1")
    subArea2: int = Field(..., title="ID de la subárea 2")


class TransmissionLineGeometry(BaseModel):
    coordinates: list[list[float]] = Field(
        ...,
        title="Coordenadas de la línea",
        description="Lista de coordenadas de la línea",
    )
    type: str = Field(
        ..., title="Tipo de geometría", description="Tipo de geometría de la línea"
    )


class TransmissionLineEntity(BaseModel):
    type: str = Field(..., title="Tipo de línea")
    properties: TransmissionLineProperties = Field(
        ..., title="Propiedades de la línea", description="Propiedades de la línea"
    )
    geometry: TransmissionLineGeometry = Field(
        ..., title="Geometría de la línea", description="Geometría de la línea"
    )


class SubstationFetchSchemaOutput(BaseModel):
    header: dict
    data: list[SubstationEntity]


class TransmissionLineFetchSchemaOutput(BaseModel):
    header: dict
    data: list[TransmissionLineEntity]
