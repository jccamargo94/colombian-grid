from typing import Optional, Any
from pydantic import BaseModel, Field


class XMMetricEntity(BaseModel):
    """Schema for XM API metric information"""

    MetricId: str = Field(..., title="Metric ID")
    MetricName: str = Field(..., title="Metric Name")
    Entity: str = Field(..., title="Entity type (Sistema, Recurso, Agente, etc.)")
    MaxDays: int = Field(..., title="Maximum days allowed per request")
    Type: str = Field(
        ...,
        title="Data type (HourlyEntities, DailyEntities, MonthlyEntities, etc.)",
    )
    Url: str = Field(..., title="API endpoint URL")
    Filter: Optional[str] = Field(None, title="Available filter options")
    MetricUnits: Optional[str] = Field(None, title="Units of measurement")
    MetricDescription: Optional[str] = Field(None, title="Metric description")


class XMMetricsListResponse(BaseModel):
    """Response schema for listing all available metrics"""

    Items: list[dict] = Field(..., title="List of metrics")
    Date: Optional[str] = Field(None, title="Response date")


class XMDataRequest(BaseModel):
    """Request schema for XM API data queries"""

    MetricId: str = Field(..., title="Metric ID to query")
    StartDate: str = Field(..., title="Start date (YYYY-MM-DD)")
    EndDate: str = Field(..., title="End date (YYYY-MM-DD)")
    Entity: str = Field(..., title="Entity type")
    Filter: Optional[list[str]] = Field(
        None, title="Optional list of filter values (e.g., resource codes)"
    )


class XMDataResponse(BaseModel):
    """Response schema for XM API data queries"""

    Items: list[dict] = Field(..., title="Data items")
    Date: Optional[Any] = Field(None, title="Response date")
