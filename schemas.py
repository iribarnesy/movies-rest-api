"""
schema.py : model to be converted in json by fastapi
"""
from typing import Optional, List
from datetime import date

from pydantic import BaseModel


class StarBase(BaseModel):
    """
    common Base Class for Stars (abstract class)
    """
    name: str
    birthdate: Optional[date]


class StarCreate(StarBase):
    """
    item witout id, only for creation purpose
    """
    pass


class Star(StarBase):
    """
    item from database with id
    """
    id: int

    class Config:
        orm_mode = True


class MovieBase(BaseModel):
    """
    common Base Class for Movies (abstract class)
    """
    title: str
    year: int
    duration: Optional[int]


class MovieCreate(MovieBase):
    """
    movies witout id, only for creation purpose
    """
    pass


class Movie(MovieBase):
    """
    movies from database with id
    """
    id: int

    class Config:
        orm_mode = True


class MovieDetail(Movie):
    """
    movies from database with director
    """
    director: Optional[Star] = None
    actors: List[Star] = []

class MovieStat(BaseModel):
    year: int
    movie_count: int
    min_duration: Optional[int]
    max_duration: Optional[int]
    avg_duration: Optional[float]

class DirectorStat(BaseModel):
    director: Star
    movie_count: int

class StarBirthyearStat(BaseModel):
    birthyear: int
    star_count: int

class StarStat(BaseModel):
    actor: Star
    movie_count : int
    first_movie_year: int
    last_movie_year: int