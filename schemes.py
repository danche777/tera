from pydantic import BaseModel

class Form(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str

class Post(BaseModel):
    access_token: str
    content: str
