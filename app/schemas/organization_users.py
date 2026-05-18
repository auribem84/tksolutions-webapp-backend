from pydantic import BaseModel

class OrgUserCreate(BaseModel):
    name: str
    email: str
    password: str
    role_id: str