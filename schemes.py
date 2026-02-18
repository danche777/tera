from pydantic import BaseModel

class Form(BaseModel):
    username: str
    password: str