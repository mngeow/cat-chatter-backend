from app.dao.schema import Persona
from typing import List
from pydantic import BaseModel

class PersonaList(BaseModel):
    personas: List[Persona]