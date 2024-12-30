from fastapi import APIRouter, Depends
from app.routes.servicesfac import get_persona_service
from app.domain.persona.service import PersonaService
from app.dao.schema import BasePersona, Persona
from app.domain.persona.schema import PersonaList

router = APIRouter()

@router.post("")
def create_persona(
    persona: BasePersona,
    persona_service: PersonaService = Depends(get_persona_service)
) -> Persona:
    return persona_service.create_persona(persona=persona)

@router.put("/{persona_id}")
def update_persona(
    persona_id: str,
    persona: BasePersona,
    persona_service: PersonaService = Depends(get_persona_service)
) -> Persona:
    return persona_service.update_persona(persona_id=persona_id, persona=persona)

@router.get("/{persona_id}")
def get_persona_by_id(
    persona_id: str,
    persona_service: PersonaService = Depends(get_persona_service)
) -> Persona:
    return persona_service.get_persona_by_id(persona_id=persona_id)

@router.get("/list")
def get_all_personas(
    persona_service: PersonaService = Depends(get_persona_service)
) -> PersonaList:
    return persona_service.get_all_personas()