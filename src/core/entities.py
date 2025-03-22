from pydantic import BaseModel


class DataEntity(BaseModel):
    id: str
    content: str
    processed: bool = False
