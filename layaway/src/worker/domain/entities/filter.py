from fastapi import Query
from pydantic import BaseModel, Field


class Filter(BaseModel):
    alphabetically: bool = Query(default=False)
    date: bool = Query(default=False)
