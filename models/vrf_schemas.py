from typing import Optional
from pydantic import BaseModel


class VrfBaseSchema(BaseModel):
    name: str
    rd: Optional[str] = None
    description: Optional[str] = None
    sections: Optional[str] = None
    customer_id: Optional[int] = None


class VrfCreateSchema(VrfBaseSchema):
    pass


class VrfUpdateSchema(VrfBaseSchema):
    pass


class VrfInDBBaseSchema(VrfBaseSchema):
    vrfId: int

    class Config:
        orm_mode = True


class VrfSchema(VrfInDBBaseSchema):
    pass
