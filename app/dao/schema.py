from pydantic import BaseModel, Field
from typing import Literal, List
from app.infrastructure.postgres.models import Chats as ChatORM, CatPersonas

class BasePersona(BaseModel):
    name: str = Field(
        description="The cat's name",
        examples=["Luna", "Milo", "Bella"]
    )
    breed: str = Field(
        description="The cat's breed",
        examples=["Siamese", "Persian", "Maine Coon"]
    )
    color_pattern: str = Field(
        description="Description of the cat's coloring and markings",
        examples=["Cream with dark points", "Orange tabby", "Tuxedo black and white"]
    )
    personality: str = Field(
        description="Key personality traits of the cat",
        examples=["Curious, chatty, and affectionate", "Shy but loving", "Independent and playful"]
    )
    favorite_activities: list[str] = Field(
        description="Activities the cat enjoys",
        examples=[["Watching birds", "Playing with strings"], ["Napping in sunbeams", "Chasing laser pointers"]]
    )
    dislikes: list[str] = Field(
        description="Things the cat dislikes or fears",
        examples=[["Vacuums", "Closed doors"], ["Water", "Loud noises"]]
    )
    quirks: list[str] = Field(
        description="Unique behavioral traits",
        examples=[["Always tries to drink from the faucet"], ["Kneads blankets while purring"]]
    )
    voice_style: str = Field(
        description="How the cat's personality comes through in their communication",
        examples=["Regal yet playful", "Shy and sweet", "Sassy and demanding"]
    )
    age: Literal["Kitten", "Adult", "Senior"] = Field(
        description="Life stage of the cat",
        examples=["Adult"]
    )


class Persona(BasePersona):
    id: str

    @property
    def to_orm(self) -> CatPersonas:
        return CatPersonas(
            persona_id = self.id,
            definition=self.model_dump(exclude={'id'})
        )
    
    @classmethod
    def from_orm(cls, orm_obj: CatPersonas) -> "Persona":
        return cls(
            id = orm_obj.persona_id,
            **orm_obj.definition
        )

class BaseChatMessage(BaseModel):
    role: Literal["user","assistant","system"]
    content: str

class BaseChat(BaseModel):
    ...

class Chat(BaseChat):
    conversation_history: List[BaseChatMessage]
    description: str | None = None
    id: str

    @property
    def to_orm(self) -> ChatORM:
        return ChatORM(
            chat_id = self.id,
            conversation_history = [item.model_dump() for item in self.conversation_history],
            description=self.description
        )
    
    @classmethod
    def from_orm(cls, orm_obj: ChatORM):
       return cls(
            id = orm_obj.chat_id,
            conversation_history = [BaseChatMessage(**item) for item in orm_obj.conversation_history],
            description=orm_obj.description
        )