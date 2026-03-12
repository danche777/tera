from pydantic import BaseModel

class Form(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str

class Post(BaseModel):
    access_token: str
    content: str

class Coment(BaseModel):
    access_token: str
    post_id: str
    comment: str

class Reaction(BaseModel):
    post_id: str
    access_token: str
    reaction: list