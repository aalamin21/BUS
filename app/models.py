from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from sqlalchemy import ForeignKey, Text
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import relationship
import json

from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from dataclasses import dataclass
from .availability_utils import default_av, group_availability

class IntegerList(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not isinstance(value, list):
                raise ValueError("Value must be a list")
            if not all(isinstance(x, int) for x in value):
                raise ValueError("All elements in the list must be integers")
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
            if not isinstance(value, list):
                raise ValueError("Stored value is not a list")
            if not all(isinstance(x, int) for x in value):
                raise ValueError("Stored value does not contain all integers")
        return value

@dataclass
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    first_name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=False)
    last_name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=False)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    faculty: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    course_name: so.Mapped[str] = so.mapped_column(sa.String(64))
    year_of_study: so.Mapped[int] = so.mapped_column(sa.Integer)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    availability: so.Mapped[list[int]] = so.mapped_column(IntegerList, default=default_av(False))
    module1: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False, default=-1)
    module2: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False, default=-1)
    module3: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False, default=-1)
    group: so.Mapped['Group'] = relationship('Group', back_populates='users')
    group_id: so.Mapped[int] = so.mapped_column(ForeignKey('groups.id'), nullable=True)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def change_time(self, time_slot):
        """
        A function to toggle the user's availability at a given time slot.
        """
        av = list(self.availability)
        av[time_slot] = 0 if av[time_slot] else 1
        self.availability = av


    def __repr__(self):
        pwh= 'None' if not self.password_hash else f'...{self.password_hash[-5:]}'
        return (f'User(id={self.id}, first_name={self.first_name},last_name={self.last_name}, email={self.email}, faculty={self.faculty},'
                f'course_name={self.course_name}, year_of_study={self.year_of_study}, pwh={pwh})')


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Group(db.Model):
    __tablename__ = 'groups'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    users: so.Mapped[list['User']] = relationship('User', back_populates='group')
    group_av: so.Mapped[list[int]] = so.mapped_column(IntegerList, default=default_av(False))
    bookings: so.Mapped[list['Booking']] = relationship('Booking', back_populates='group', cascade='all, delete-orphan')

    def update_availability(self):
        """
        A function that updates the availability list for this group. If the group is empty it stores a zero availability
        list.
        """
        try:
            self.group_av = group_availability(*(user.availability for user in self.users if user.availability))
        except IndexError:
            self.group_av = default_av(False)

    def add_user(self, user: User):
        """
        A function to add a user to the group as well as update the group availability list.
        """
        self.users.append(user)
        # Combine availability using logical AND
        self.group_av = self.group_av if self.group_av else default_av(True)
        self.update_availability()

    def remove_user(self, user: User):
        """
        A function to remove a user from the group as well as update the group availability list.
        """
        self.users.remove(user)
        user.group_id = None
        self.update_availability()
        if not self.users:
            db.session.delete(self)
    def __repr__(self):
        return f'Group(id={self.id}), Members: {self.members}'

class Booking(db.Model):
    __tablename__ = 'bookings'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    group_id: so.Mapped[int] = so.mapped_column(ForeignKey('groups.id'))
    group: so.Mapped['Group'] = relationship('Group', back_populates='bookings')
    time_slot: so.Mapped[int] = so.mapped_column(sa.Integer)
    room: so.Mapped[str] = so.mapped_column(sa.String(256))

