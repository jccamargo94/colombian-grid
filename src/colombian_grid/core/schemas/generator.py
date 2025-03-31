from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class GeneratorType(str, Enum):
    EOLICA = "eólica"
    SOLAR = "solar"
    TERMICA = "térmica"
    HIDRAULICA = "hidráulica"


class OperationModeType(str, Enum):
    DESPACHADA = "Despachada Centralmente"
    NO_DESPACHADA = "No Despachada Centralmente"


class GeneratorEntity(BaseModel):
    type: GeneratorType = Field(..., title="Tipo de generador")
    lat: Optional[float] = Field(..., title="Latitud")
    lng: Optional[float] = Field(..., title="Longitud")
    iconAsset: Optional[str] = Field(..., title="Icono")
    subArea: Optional[str] = Field(..., title="Subárea")
    elementName: Optional[str] = Field(..., title="Nombre del generador")
    operatorCompanyName: Optional[str] = Field(
        ..., title="Nombre de la empresa operadora"
    )
    operationMode: OperationModeType = Field(..., title="Modo de operación")
    netEffectiveCapacity: Optional[float] = Field(..., title="Capacidad efectiva neta")
    fpoDate: Optional[str] = Field(None, title="Fecha de puesta en operación")
    operatingProcessType: Optional[str] = Field(
        ..., title="Tipo de proceso de operación"
    )
    connectionVoltage: Optional[float] = Field(..., title="Voltaje de conexión")
    ratedPower: Optional[float] = Field(..., title="Potencia nominal")
    powerMax: Optional[float] = Field(..., title="Potencia máxima")
    department: Optional[str] = Field(..., title="Departamento")
    municipality: Optional[str] = Field(..., title="Municipio")


class GeneratorFetchSchemaOutput(BaseModel):
    header: dict
    data: list[GeneratorEntity]
