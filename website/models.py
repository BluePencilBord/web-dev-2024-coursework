from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column

class Role(db.Model):
    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(db.String(64), nullable=False, unique=True)
    description : Mapped[str] = mapped_column(db.String(100), nullable=False, unique=True)

    users : Mapped[list['User']] = db.relationship(back_populates='role', uselist=True)

class User(db.Model, UserMixin):
    id : Mapped[int] = mapped_column(primary_key=True)
    login : Mapped[str] = mapped_column(db.String(32), unique=True, nullable=False)
    password_hash : Mapped[str] = mapped_column(db.String(300), nullable=False)
    last_name : Mapped[str] = mapped_column(db.String(64), nullable=False)
    first_name : Mapped[str] = mapped_column(db.String(64), nullable=False)
    middle_name : Mapped[str] = mapped_column(db.String(64))
    role_id : Mapped[int] = mapped_column(db.ForeignKey('role.id'))

    role : Mapped['Role'] = db.relationship(back_populates='users', uselist=False)
    reviews : Mapped[list['Review']] = db.relationship(back_populates='user', uselist=True)

class Recipe(db.Model):
    id : Mapped[int] = mapped_column(primary_key=True)
    title : Mapped[str] = mapped_column(db.String(200), unique=True, nullable=False)
    description : Mapped[str] = mapped_column(db.Text, nullable=False)
    time_to_cook : Mapped[int] = mapped_column(nullable=False)
    photo_id : Mapped[int] = mapped_column(db.ForeignKey('photo.id'))

    photo : Mapped['Photo'] = db.relationship(back_populates='recipes', uselist=False)
    reviews : Mapped[list['Review']] = db.relationship(back_populates='recipe', uselist=True, cascade='all, delete-orphan')

class Photo(db.Model):
    id : Mapped[int] = mapped_column(primary_key=True)
    file_name : Mapped[str] = mapped_column(db.String(200), nullable=False)
    MIME_type : Mapped[str] = mapped_column(db.String(200), nullable=False)
    MD5_hash : Mapped[str] = mapped_column(db.String(200), nullable=False)

    recipes : Mapped[list['Recipe']] = db.relationship(back_populates='photo', uselist=True)

class Review(db.Model):
    recipe_id : Mapped[int] = mapped_column(db.ForeignKey('recipe.id'), primary_key=True)
    user_id : Mapped[int] = mapped_column(db.ForeignKey('user.id'), primary_key=True)
    score : Mapped[int] = mapped_column(nullable=False)
    text : Mapped[int] = mapped_column(db.Text, nullable=False)
    creation_date : Mapped[int] = mapped_column(db.TIMESTAMP, default=func.now())

    recipe : Mapped['Recipe'] = db.relationship(back_populates='reviews', uselist=False)
    user : Mapped['User'] = db.relationship(back_populates='reviews', uselist=False)