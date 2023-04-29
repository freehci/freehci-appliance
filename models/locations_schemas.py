from pydantic import BaseModel

class LocationBaseSchema(BaseModel):
    name: str
    description: str = None
    address: str = None
    lat: str = None
    long: str = None

class LocationCreateSchema(LocationBaseSchema):
    pass

class LocationSchema(LocationBaseSchema):
    id: int

    class Config:
        orm_mode = True
