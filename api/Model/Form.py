from pydantic import BaseModel
from typing import Optional,List

class Form_complet(BaseModel):
    id:str
    img:str="defult_img.jpg"
    title:str
    text:str
    group:str
    attachment:Optional[List[str]]=None



class Form_insert(BaseModel):
    img:str="defult_img.jpg"
    title:str
    text:str
    group:str
    attachment:Optional[List[str]]=None




class FormGroup(BaseModel):
    name:str
    img:str






