from typing import Optional, Dict
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from dataclasses import dataclass
import datetime
from app.static.dt_lists import days, time_slots

def default_av():
    av = {}

    for day_code, day_name in days:
        av[day_code] = {}
        for time_code, time_name in time_slots:
            av[day_code][time_code] = False
    return av

@dataclass
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    first_name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    last_name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    faculty: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    course_name: so.Mapped[str] = so.mapped_column(sa.String(64))
    year_of_study: so.Mapped[int] = so.mapped_column(sa.Integer)
    password: so.Mapped[str] = so.mapped_column(sa.String(128))
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    #role: so.Mapped[str] = so.mapped_column(sa.String(10), default="Normal")
    availability: so.Mapped[Dict[str, Dict[str, bool]]] = so.mapped_column(sa.JSON, default=default_av())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        pwh= 'None' if not self.password_hash else f'...{self.password_hash[-5:]}'
        return (f'User(id={self.id}, first_name={self.first_name},last_name={self.last_name}, email={self.email}, faculty={self.faculty},'
                f'course_name={self.course_name}, year_of_study={self.year_of_study}, pwh={pwh})')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))