from typing import Optional

from pydantic import BaseModel, Field


class HydroEntity(BaseModel):
    type: str = Field("embalse", description="Tipo de entidad")
    lat: Optional[float] = Field(
        None, description="Latitud de la entidad hidroeléctrica"
    )
    lng: Optional[float] = Field(
        None, description="Longitud de la entidad hidroeléctrica"
    )
    reservoirMRID: Optional[int] = Field(None, description="Embalse MRID")
    elementName: Optional[str] = Field(..., description="Nombre del elemento")
    operatorCompanyName: Optional[str] = Field(
        ..., description="Nombre de la empresa propietaria"
    )
    fpoDate: Optional[str] = Field(None, description="Fecha de puesta en operación")
    isReservoirAggregate: Optional[str] = Field(
        None, description="¿Es un embalse agregado?"
    )
    hidrologicalRegion: Optional[str] = Field(..., description="Región hidrológica")
    minPhysicalLevel: Optional[float] = Field(None, description="Nivel mínimo físico")
    minTechnicalLevel: Optional[float] = Field(None, description="Nivel mínimo técnico")
    maxPhysicalLevel: Optional[float] = Field(None, description="Nivel máximo físico")
    deadVolume: Optional[float] = Field(None, description="Volumen muerto")
    minTechnicalVolume: Optional[float] = Field(
        None, description="Volumen mínimo técnico"
    )
    maxTechnicalVolume: Optional[float] = Field(
        None, description="Volumen máximo técnico"
    )
    usefulVolume: Optional[float] = Field(None, description="Volumen útil")
    totalVolume: Optional[float] = Field(None, description="Volumen total")
    convertionFactor: Optional[float] = Field(None, description="Factor de conversión")
    usefulVolumeGWh: Optional[float] = Field(None, description="Volumen útil en GWh")


class HydroFetchSchemaOutput(BaseModel):
    header: dict
    data: list[HydroEntity]
