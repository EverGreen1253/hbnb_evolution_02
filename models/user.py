#!/usr/bin/python

from datetime import datetime
import uuid
import re
import json
from flask import jsonify, request, abort
from sqlalchemy import Column, String, DateTime
from data import storage, use_db_storage, Base

class User(Base):
    """Representation of user """

    # Class attrib defaults
    id = None
    created_at = None
    updated_at = None
    __first_name = ""
    __last_name = ""
    __email = ""
    __password = ""

    if use_db_storage:
        __tablename__ = 'users'
        id = Column(String(60), nullable=False, primary_key=True)
        created_at = Column(DateTime, nullable=False, default=datetime.now().timestamp())
        updated_at = Column(DateTime, nullable=False, default=datetime.now().timestamp())
        __first_name = Column("first_name", String(128), nullable=True, default="")
        __last_name = Column("last_name", String(128), nullable=True, default="")
        __email = Column("email", String(128), nullable=False)
        __password = Column("password", String(128), nullable=False)
        # places = relationship("Place", back_populates="user",cascade="delete, delete-orphan")
        # reviews = relationship("Review", back_populates="user",cascade="delete, delete-orphan")

    # Constructor
    def __init__(self, *args, **kwargs):
        """ constructor """
        # Set object instance defaults
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at

        # Only allow first_name, last_name, email, password.
        # Note that setattr will call the setters for these attribs
        if kwargs:
            for key, value in kwargs.items():
                if key in ["first_name", "last_name", "email", "password"]:
                    setattr(self, key, value)

    # --- Getters and Setters ---
    @property
    def first_name(self):
        """Getter for private prop first_name"""
        return self.__first_name

    @first_name.setter
    def first_name(self, value):
        """Setter for private prop first_name"""

        # ensure that the value is alphabets only
        # Note that this won't allow names like Obi-wan or Al'azif
        is_valid_name = len(value.strip()) > 0 and re.search("^[a-zA-Z]+$", value)
        if is_valid_name:
            self.__first_name = value
        else:
            raise ValueError("Invalid first name specified: {}".format(value))

    @property
    def last_name(self):
        """Getter for private prop last_name"""
        return self.__last_name

    @last_name.setter
    def last_name(self, value):
        """Setter for private prop last_name"""

        # ensure that the value is alphabets only
        # Note that this won't allow names like Obi-wan or Al'azif
        is_valid_name = len(value.strip()) > 0 and re.search("^[a-zA-Z]+$", value)
        if is_valid_name:
            self.__last_name = value
        else:
            raise ValueError("Invalid last name specified: {}".format(value))

    @property
    def email(self):
        """Getter for private prop email"""
        return self.__email

    @email.setter
    def email(self, value):
        """Setter for private prop last_name"""

        # add a simple regex check for email format. Nothing too fancy.
        is_valid_email = len(value.strip()) > 0 and re.search("^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$", value)
        if is_valid_email:
            self.__email = value
        else:
            raise ValueError("Invalid email specified: {}".format(value))

    @property
    def password(self):
        """Getter for private prop email"""
        return self.__password

    @password.setter
    def password(self, value):
        """Setter for private prop email"""
        is_valid_password = len(value) >= 6
        if is_valid_password:
            self.__password = value
        else:
            raise ValueError("Password is too short! Min 6 characters required.")

    # --- Static methods ---
    @staticmethod
    def all():
        """ Class method that returns all users data"""
        data = []
        user_data = storage.get('User')

        # Data loaded from the DB needs additional cleanup before it can be used
        if use_db_storage:
            user_data = User.to_dict(user_data)

        for k, v in user_data.items():
            data.append({
                "id": v['id'],
                "first_name": v['first_name'],
                "last_name": v['last_name'],
                "email": v['email'],
                "password": v['password'],
                "created_at": datetime.fromtimestamp(v['created_at']),
                "updated_at": datetime.fromtimestamp(v['updated_at'])
            })

        return jsonify(data)

    @staticmethod
    def specific(user_id):
        """ Class method that returns a specific user's data"""
        data = []
        user_data = storage.get('User')

        if user_id not in user_data:
            # raise IndexError("User not found!")
            return "User not found!"

        v = user_data[user_id]
        data.append({
            "id": v['id'],
            "first_name": v['first_name'],
            "last_name": v['last_name'],
            "email": v['email'],
            "password": v['password'],
            "created_at": datetime.fromtimestamp(v['created_at']),
            "updated_at": datetime.fromtimestamp(v['updated_at'])
        })

        return jsonify(data)

    @staticmethod
    def create():
        """ Class method that creates a new user"""
        if request.get_json() is None:
            abort(400, "Not a JSON")

        data = request.get_json()
        if 'email' not in data:
            abort(400, "Missing email")
        if 'password' not in data:
            abort(400, "Missing password")

        try:
            u = User(
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                password=data["password"]
            )
        except ValueError as exc:
            return repr(exc) + "\n"

        attribs = {
            "id": u.id,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "email": u.email,
            "created_at": u.created_at,
            "updated_at": u.updated_at
        }

        # add to whatever is in storage at the moment
        storage.add('User', attribs)

        # print the Users out and you'll see the new one has been added
        # print(storage.get('User'))

        # update the created_at and updated_at to something readable before passing it out for display
        attribs['created_at'] = datetime.fromtimestamp(u.created_at)
        attribs['updated_at'] = datetime.fromtimestamp(u.updated_at)

        return jsonify(attribs)

    @staticmethod
    def update(user_id):
        """ Class method that updates an existing user"""
        if request.get_json() is None:
            abort(400, "Not a JSON")

        data = request.get_json()
        user_data = storage.get("User")

        if user_id not in user_data:
            abort(400, "User not found for id {}".format(user_id))

        u = storage.get("User", user_id)

        # modify the values
        for k, v in data.items():
            # only first_name and last_name are allowed to be modified
            if k in ["first_name", "last_name"]:
                u[k] = v

        attribs = {
            "id": u["id"],
            "first_name": u["first_name"],
            "last_name": u["last_name"],
            "email": u["email"],
            "created_at": u["created_at"],
            "updated_at": u["updated_at"]
        }

        # update the User record with the new first_name and last_name
        storage.update('User', user_id, attribs)

        # print the Users out and you'll see the record has been updated
        # print(storage.get('User'))

        # update the created_at and updated_at to something readable before passing it out for display
        attribs['created_at'] = datetime.fromtimestamp(u["created_at"])
        attribs['updated_at'] = datetime.fromtimestamp(u["updated_at"])

        # print out the updated user details
        return jsonify(attribs)

    @staticmethod
    def to_dict(data):
        """ Perform cleanup on raw DB data and return as dictionary"""
        # TODO:
        print(data.__dict__)
        return data