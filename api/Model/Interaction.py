from pydantic import BaseModel

class like(BaseModel):
    id:str
    user:str
    type_post:str
    post_id:str

class like_insert(BaseModel):
    user:str
    type_post:str
    post_id:str


class comment(BaseModel):
    comment:str
    user:str
    type_post:str
    post_id:str

class comment_get(BaseModel):
    id:str
    comment:str
    user:str
    type_post:str
    post_id:str

