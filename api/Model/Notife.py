from pydantic import BaseModel

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
