from pydantic import BaseModel, Field


class Film(BaseModel):
    name: str
    description: str
    rating: float = Field(ge=0, le=10)
    genre: str
    year: int = Field(ge=1888, le=2100)
    actors: list[str]
    poster: str