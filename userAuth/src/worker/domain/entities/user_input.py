from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, schema, validator
from pydantic.fields import ModelField


def field_schema(field: ModelField, **kwargs: Any) -> Any:
    if field.field_info.extra.get('hidden_from_schema', False):
        raise schema.SkipField(f'{field.name} field is being hidden')
    else:
        return original_field_schema(field, **kwargs)


original_field_schema = schema.field_schema
schema.field_schema = field_schema

special_characters = "~!@#$%^&*_-+=`|\(){}[]:;'<>,.?/"


class UserRegistration(BaseModel):
    id: UUID = Field(default_factory=uuid4, hidden_from_schema=True)
    name: str
    age: int
    username: str
    password: str

    @validator('name', 'username', pre=True)
    def validate_name(cls, v):
        if isinstance(v, int):
            raise ValueError('must be str')
        if v.isnumeric():
            raise ValueError('must not be a numeric field')
        return v

    @validator('age', pre=True)
    def validate_age(cls, v):
        if v <= 0 or v >= 100:
            raise ValueError('invalid age')
        return v

    @validator('password', pre=True)
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('must be at least 8 characters long')
        if not any(character.isupper() for character in v):
            raise ValueError('should contain at least one uppercase character')
        if not any(character.isdigit() for character in v):
            raise ValueError('should contain at least one digit')
        if all(character not in special_characters for character in v):
            raise ValueError('should contain at least one special character')
        return v


class UserLogin(BaseModel):
    username: str
    password: str

    @validator('username', pre=True)
    def validate_name(cls, v):
        if isinstance(v, int):
            raise ValueError('must be str')
        if v.isnumeric():
            raise ValueError('must not be a numeric field')
        return v

    @validator('password', pre=True)
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('must be at least 8 characters long')
        if not any(character.isupper() for character in v):
            raise ValueError('should contain at least one uppercase character')
        if not any(character.isdigit() for character in v):
            raise ValueError('should contain at least one digit')
        if all(character not in special_characters for character in v):
            raise ValueError('should contain at least one special character')
        return v
