from pydantic import BaseModel


class Character(BaseModel):
    id: int
    name: str
    image: str
    appearances: int
