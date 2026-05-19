from pydantic import BaseModel
from typing import Optional,List, Dict, Any

class Field(BaseModel):
    label: str
    type: str
    required: bool
    options: Optional[List[str]] = None

class FormCreate(BaseModel):
    name: str
    moavenat:str
    type_form:str
    show:bool=False
    fields: List[Field]

class SubmissionCreate(BaseModel):
    data: Dict[str, Any]