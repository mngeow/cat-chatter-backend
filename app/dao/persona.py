from sqlalchemy.orm import scoped_session
from .schema import Persona
from app.infrastructure.postgres.models import CatPersonas
from sqlalchemy import select, update
from typing import List

class PersonaDAO:
    def __init__(self, db_session: scoped_session) -> None:
        self._db_session = db_session
    
    def create(self, persona: Persona) -> Persona:
        orm_obj = persona.to_orm

        self._db_session.add(orm_obj)
        self._db_session.flush()
        self._db_session.refresh(orm_obj)

        return Persona.from_orm(orm_obj=orm_obj)
    
    def update(self, persona: Persona) -> None:
        stmt = update(CatPersonas).where(CatPersonas.persona_id == persona.id).values(
            definition=persona.model_dump(exclude={'id'})
        )
        self._db_session.execute(stmt)
        self._db_session.commit()
    
    def fetch_personas(self) -> List[Persona]:
        stmt = select(CatPersonas)
        result_proxy = self._db_session.execute(stmt)
        res = result_proxy.scalars().all()

        return [Persona.from_orm(orm_obj=item) for item in res]
    
    def get_persona_by_id(self, persona_id: str) -> Persona:
        stmt = select(CatPersonas).filter_by(persona_id=persona_id)
        result_proxy = self._db_session.execute(stmt)
        res = result_proxy.scalars().first()

        return Persona.from_orm(orm_obj=res)