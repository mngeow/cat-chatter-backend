from sqlalchemy.orm import scoped_session
from app.dao.persona import PersonaDAO
from app.dao.schema import BasePersona, Persona
from .schema import PersonaList
import uuid

class PersonaService:
    def __init__(self, db_session: scoped_session) -> None:
        self._persona_dao = PersonaDAO(db_session=db_session)
    
    def create_persona(self, persona: BasePersona) -> Persona:
        persona_obj = Persona(
            id=str(uuid.uuid4()),
            **persona.model_dump()
        )

        return self._persona_dao.create(persona=persona_obj)
    
    def get_persona_by_id(self, persona_id: str) -> Persona:
        return self._persona_dao.get_persona_by_id(persona_id=persona_id)
    
    def update_persona(self, persona_id: str, persona: BasePersona) -> Persona:
        persona_obj = Persona(
            id=persona_id,
            **persona.model_dump()
        )

        self._persona_dao.update(persona=persona_obj)

        return persona_obj
    
    def get_all_personas(self) -> PersonaList:
        return PersonaList(
            personas=self._persona_dao.fetch_personas()
        )