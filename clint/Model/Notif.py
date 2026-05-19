from pydantic import BaseModel
from typing import Optional,List
class Notife_complet(BaseModel):
    id:str
    img:str
    title:str
    text:str
    show:bool
    important:bool
    secret:bool
    moavenat:str
    attachment:list[str]
    comment:bool=False
    like:bool=False


class Notife_insert(BaseModel):
    img:str="defult.jpg"
    title:str
    text:str
    show:bool=False
    important:bool=False
    comment:bool=False
    like:bool=False
    secret:bool=False
    moavenat:str
    attachment:Optional[List[str]]=None
    # attachment:list[str]

class Notife_insert_edite(BaseModel):
    img:str="not_new"
    title:str
    text:str
    show:bool=False
    important:bool=False
    secret:bool=False
    moavenat:str
    attachment:list[str]=["not_new_attach"]
    comment:bool=False
    like:bool=False
