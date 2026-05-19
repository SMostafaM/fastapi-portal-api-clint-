from pydantic import BaseModel
from typing import Optional,List, Dict, Any

class Field(BaseModel):
    # id: str
    label: str
    type: str
    required: bool
    options: Optional[List[str]] = None

class Field_in(BaseModel):
    label: str
    type: str
    required: bool
    options: Optional[List[str]] = None

class FormCreate(BaseModel):
    id:str
    name: str
    moavenat:str
    type_form:str
    show:bool
    fields: List[Field]

class FormCreate_insert(BaseModel):
    name: str
    moavenat:str
    type_form:str
    show:bool
    fields: List[Field_in]

class SubmissionCreate(BaseModel):
    form_id:str
    name: str
    moavenat:str
    type_form:str
    data: Dict[str, Any]