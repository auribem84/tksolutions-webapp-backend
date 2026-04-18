from pydantic import BaseModel


class ServiceCreate(BaseModel):
    name: str


class ServiceOut(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True