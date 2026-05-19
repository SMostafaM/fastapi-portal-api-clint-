from pydantic import BaseModel

class User_complet(BaseModel):
    # number:str
    id:str
    username:str
    password:str
    type_user:str
    # verificate_number:bool = False

class User_insert(BaseModel):
    # number:str
    # email:str
    username:str
    password:str
    type_user:str

class User_plus(BaseModel):
    name:str
    img:str="defult.jpg"
    username:str
    password:str
    type_user:str
class User_plus_complte(BaseModel):
    id:str
    name:str
    img:str="defult_user.jpg"
    username:str
    password:str
    type_user:str

class User_login(BaseModel):
    username:str
    password:str

class Active_session(BaseModel):
    username:str
    token:str

# class Verificate(BaseModel):
#     number:str
#     verificate_code:str