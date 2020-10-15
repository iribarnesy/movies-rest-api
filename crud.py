"""
file crud.py
manage CRUD and adapt model data from db to schema data to api rest
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, extract, between
from sqlalchemy import func
from fastapi.logger import logger
import models
import schemas

# CRUD for Movie objects


def get_movie(db: Session, movie_id: int):
    # read from the database (get method read from cache)
    # return object read or None if not found
    db_movie = db.query(models.Movie).filter(
        models.Movie.id == movie_id).first()
    return db_movie


def get_movies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Movie).offset(skip).limit(limit).all()


def create_movie(db: Session, movie: schemas.MovieCreate):
    db_movie = models.Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


def update_movie(db: Session, movie: schemas.Movie):
    db_movie = get_movie(db=db, movie_id=movie.id)
    if db_movie is None:
        return None
    for key, value in movie.dict().items():
        setattr(db_movie, key, value)
    db.commit()
    return db_movie


def delete_movie(db: Session, movie_id: int):
    db_movie = get_movie(db=db, movie_id=movie_id)
    if db_movie is None:
        return None
    db.delete(db_movie)
    db.commit()
    return db_movie


def _get_movies_by_predicate(*predicate, db: Session):
    """ partial request to apply one or more predicate(s) to model Movie"""
    return db.query(models.Movie)   \
        .filter(*predicate)


def get_movies_by_title(db: Session, title: str):
    return _get_movies_by_predicate(models.Movie.title == title, db=db)    \
        .order_by(desc(models.Movie.year))                      \
        .all()


def get_movies_by_title_part(db: Session, title: str):
    return _get_movies_by_predicate(models.Movie.title.like(f'%{title}%'), db=db)   \
        .order_by(models.Movie.title, models.Movie.year)                       \
        .all()


def get_movies_by_year(db: Session, year: int):
    return _get_movies_by_predicate(models.Movie.year == year, db=db)    \
        .order_by(models.Movie.title)                         \
        .all()


def get_movies_by_range_year(db: Session, year_min: Optional[int], year_max: Optional[int]):
    if year_min is None and year_max is None:
        return None
    if year_min is None:
        predicate = models.Movie.year <= year_max
    elif year_max is None:
        predicate = models.Movie.year >= year_min
    else:
        predicate = between(models.Movie.year, year_min, year_max)
    return _get_movies_by_predicate(predicate, db=db)                  \
        .order_by(models.Movie.year, models.Movie.title)    \
        .all()


def get_movies_by_title_year(db: Session, title: str, year: int):
    return _get_movies_by_predicate(
        models.Movie.title == title,
        models.Movie.year == year,
        db=db)                                      \
        .order_by(models.Movie.year, models.Movie.title)    \
        .all()


def get_movies_count(db: Session):
    return db.query(models.Movie).count()


def get_movies_count_year(db: Session, year: int):
    return _get_movies_by_predicate(models.Movie.year == year, db=db).count()


def get_movies_by_director_endname(db: Session, endname: str):
    return db.query(models.Movie).join(models.Movie.director)      \
        .filter(models.Star.name.like(f'%{endname}')) \
        .order_by(desc(models.Movie.year))  \
        .all()


def get_movies_by_actor_endname(db: Session, endname: str):
    return db.query(models.Movie).join(models.Movie.actors) \
        .filter(models.Star.name.like(f'%{endname}'))   \
        .order_by(desc(models.Movie.year))              \
        .all()


def get_stats_movies_count_by_year(db: Session):
    query = db.query(models.Movie.year,
                     func.count().label("movie_count"),
                     func.min(models.Movie.duration).label("min_duration"),
                     func.max(models.Movie.duration).label("max_duration"),
                     func.avg(models.Movie.duration).label("avg_duration")) \
        .group_by(models.Movie.year)    \
        .order_by(models.Movie.year)
    return [{'year': y, 'movie_count': mc, 'min_duration': mind, 'max_duration': maxd, 'avg_duration': avgd} for y, mc, mind, maxd, avgd in query]


# CRUD association


def update_movie_director(db: Session, movie_id: int, director_id: int):
    db_movie = get_movie(db=db, movie_id=movie_id)
    db_star = get_star(db=db, star_id=director_id)
    if db_movie is None or db_star is None:
        return None
    # update object association
    db_movie.director = db_star
    # commit transaction : update SQL
    db.commit()
    # return updated object
    return db_movie

def update_movie_actors(db: Session, movie_id: int, stars_id: List[int]):
    db_movie = get_movie(db=db, movie_id=movie_id)
    if db_movie is None:
        return None
    db_movie.actors = []
    for sid in stars_id:
        db_star = get_star(db=db, star_id=sid)
        if db_star is None:
            return None
        db_movie.actors.append(db_star)
    db.commit()
    return db_movie

def add_movie_actor(db: Session, movie_id: int, star_id: int):
    db_movie = get_movie(db=db, movie_id=movie_id)
    db_star = get_star(db=db, star_id=star_id)
    if db_movie is None or db_star is None:
        return None
    db_movie.actors.append(db_star)
    db.commit()
    return db_movie


def get_stats_movie_by_director(db: Session, min_count: int = 10):
    query = db.query(models.Star,
                     func.count(models.Movie.id).label("movie_count"))
    query = query.join(models.Movie.director) \
        .group_by(models.Star) \
        .having(func.count(models.Movie.id) >= min_count) \
        .order_by(desc("movie_count"))
    return [{"director": director, "movie_count": mc} for director, mc in query]

# CRUD for Star objects


def _get_stars_by_predicate(*predicate, db: Session):
    """ partial request to apply one or more predicate(s) to model Star"""
    return db.query(models.Star)   \
        .filter(*predicate)


def get_star(db: Session, star_id: int):
    # read from the database (get method read from cache)
    # return object read or None if not found
    return db.query(models.Star).filter(models.Star.id == star_id).first()
    # return db.query(models.Star).get(1)
    # return schemas.Star(id=1, name="Fred")


def get_stars(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Star).offset(skip).limit(limit).all()


def create_star(db: Session, star: schemas.StarCreate):
    db_star = models.Star(name=star.name, birthdate=star.birthdate)
    db.add(db_star)
    db.commit()
    db.refresh(db_star)
    return db_star


def update_star(db: Session, star: schemas.Star):
    db_star = get_star(db=db, star_id=star.id)
    if db_star is None:
        return None
    for key, value in star.dict().items():
        setattr(db_star, key, value)
    db.commit()
    return db_star


def delete_star(db: Session, star_id: int):
    db_star = get_star(db=db, star_id=star_id)
    if db_star is None:
        return None
    db.delete(db_star)
    db.commit()
    return db_star


def get_stars_by_name(db: Session, name: str):
    return _get_stars_by_predicate(models.Star.name == name, db=db) \
        .order_by(models.Star.birthdate)  \
        .all()


def get_stars_by_endname(db: Session, name: str):
    return _get_stars_by_predicate(models.Star.name.like(f'%{name}'), db=db) \
        .order_by(models.Star.birthdate)  \
        .all()


def get_stars_by_birthyear(db: Session, year: int):
    return _get_stars_by_predicate(extract('year', models.Star.birthdate) == year, db=db) \
        .order_by(models.Star.name)  \
        .all()


def get_stars_count(db: Session):
    return db.query(models.Star).count()


def get_star_director_movie(db: Session, movie_id: int):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id)  \
        .join(models.Movie.director).first()
    if db_movie is not None:
        return db_movie.director
    else:
        return None


def get_star_director_movie_by_title(db: Session, title: str):
    db_movies = db.query(models.Movie).filter(models.Movie.title.like(f'%{title}%')) \
        .join(models.Movie.director)
    return [db_movie.director for db_movie in db_movies]
