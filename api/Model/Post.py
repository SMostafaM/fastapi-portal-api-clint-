from pydantic import BaseModel
from typing import Optional,List
class Post_complet(BaseModel):
    id:str
    img:str="defult_img.jpg"
    title:str
    text:str
    show:bool=False
    comment:bool=False
    like:bool=False
    # moavenat:str
    attachment:Optional[List[str]]=None
    tag:Optional[List[str]]=None
    username:str
    username:str


class Post_insert(BaseModel):
    img:str="defult_img.jpg"
    title:str
    text:str
    show:bool=False
    comment:bool=False
    like:bool=False
    # moavenat:str
    attachment:Optional[List[str]]=None
    tag:Optional[List[str]]=None
    username:str
    # attachment:list[str]



class Tag(BaseModel):
    tag:str
    img:str






