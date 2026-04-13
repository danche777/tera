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
    access_token: str
    post_id: str
    reaction: str

class DeletePost(BaseModel):
    access_token: str
    post_id: str

class Count_pages(BaseModel):
    count_pages: int