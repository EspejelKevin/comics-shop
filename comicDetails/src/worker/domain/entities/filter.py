from typing import Optional

from pydantic import BaseModel


class Filter(BaseModel):
    contains: Optional[str]
    page: Optional[int]
    comic: Optional[str]
    number: Optional[int]
    year: Optional[int]
    character: Optional[str]
