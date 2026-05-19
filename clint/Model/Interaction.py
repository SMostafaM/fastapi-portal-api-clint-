from pydantic import BaseModel

class like(BaseModel):
    id:str
    user:str
    type_post:str
    post_id:str




class Comment(BaseModel):
    comment:str
    user:int
    type_post:str
    post_id:str

