from typing import Optional

from pydantic import BaseModel, root_validator, validator


class ComicInput(BaseModel):
    id: int

    @root_validator(pre=True)
    def validate_body(cls, values):
        if not values:
            raise ValueError('there must be at least one parameter')
        return values
