#!/usr/bin/python
""" Place models """

from datetime import datetime
import uuid
import re
from flask import jsonify, request, abort
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from data import storage, USE_DB_STORAGE, Base

# This is unfortunately the best possible way to have the many-to-many relationship work both ways.
# If the two classes are split into separate files, you'll have to import the other class
# to make things work, and this would cause a circular import error (chicken and egg problem).


if USE_DB_STORAGE:
    # define the many-to-many table
    place_amenity = Table(
        'place_amenity',
        Base.metadata,
        Column('place_id', String(60), ForeignKey('places.id'), primary_key=True),
        Column('amenity_id', String(60), ForeignKey('amenities.id'), primary_key=True)
    )


class Place(Base):
    """Representation of place """

    datetime_format = "%Y-%m-%dT%H:%M:%S.%f"

    # Class attrib defaults
    id = None
    created_at = None
    updated_at = None
    __city_id = ""
    __host_id = ""
    __name = ""
    __description = ""
    __address = ""
    __number_of_rooms = 0
    __number_of_bathrooms = 0
    __max_guests = 0
    __price_per_night = 0
    __latitude = 0
    __longitude = 0

    if USE_DB_STORAGE:
        __tablename__ = 'places'
        id = Column(String(60), nullable=False, primary_key=True)
        created_at = Column(DateTime, nullable=False, default=datetime.now())
        updated_at = Column(DateTime, nullable=False, default=datetime.now())
        __city_id = Column("city_id", String(60), ForeignKey('cities.id'), nullable=False)
        __host_id = Column("host_id", String(60), ForeignKey('users.id'), nullable=False)
        __name = Column("name", String(128), nullable=False)
        __description = Column("description", String(1024), nullable=True)
        __address = Column("address", String(1024), nullable=True)
        __number_of_rooms = Column("number_of_rooms", Integer, nullable=False, default=0)
        __number_of_bathrooms = Column("number_of_bathrooms", Integer, nullable=False, default=0)
        __max_guests = Column("max_guests", Integer, nullable=False, default=0)
        __price_per_night = Column("price_per_night", Integer, nullable=False, default=0)
        __latitude = Column("latitude", Float, nullable=True)
        __longitude = Column("longitude", Float, nullable=True)
        amenities = relationship("Amenity", secondary=place_amenity, back_populates = 'places')
        # reviews = relationship("Review", back_populates="place")
        # owner = relationship("User", back_populates="properties")

    # Constructor
    def __init__(self, *args, **kwargs):
        """ constructor """
        # Set object instance defaults
        self.id = str(uuid.uuid4())

        # Note that db records have a default of datetime.now()
        if not USE_DB_STORAGE:
            self.created_at = datetime.now().timestamp()
            self.updated_at = self.created_at

        # Only allow whatever is in can_init_list.
        # Note that setattr will call the setters for these attribs
        if kwargs:
            for key, value in kwargs.items():
                if key in ["city_id", "host_id", "name", "description", "number_rooms", "number_bathrooms", "max_guest", "price_by_night", "latitude", "longitude"]:
                    setattr(self, key, value)

    @property
    def city_id(self):
        """ Returns value of private property city_id """
        return self.__city_id

    @city_id.setter
    def city_id(self, value):
        """Setter for private prop city_id"""
        self.__city_id = value

    @property
    def host_id(self):
        """ Returns value of private property host_id """
        return self.__host_id

    @host_id.setter
    def host_id(self, value):
        """Setter for private prop host_id"""
        self.__host_id = value

    @property
    def name(self):
        """ Returns value of private property name """
        return self.__name

    @name.setter
    def name(self, value):
        """Setter for private prop name"""
        # Can't think of any special checks to perform here tbh
        self.__name = value

    @property
    def description(self):
        """ Returns value of private property description """
        return self.__description

    @description.setter
    def description(self, value):
        """Setter for private prop description"""
        # Can't think of any special checks to perform here tbh
        self.__description = value

    @property
    def address(self):
        """ Returns value of private property address """
        return self.__address

    @address.setter
    def address(self, value):
        """Setter for private prop address"""
        # Can't think of any special checks to perform here tbh
        self.__address = value

    @property
    def number_of_rooms(self):
        """ Returns value of private property number_of_rooms """
        return self.__number_of_rooms

    @number_of_rooms.setter
    def number_of_rooms(self, value):
        """Setter for private prop number_of_rooms"""
        if isinstance(value, int):
            self.__number_of_rooms = value
        else:
            raise ValueError("Invalid value specified for Number of Rooms: {}".format(value))

    @property
    def number_of_bathrooms(self):
        """ Returns value of private property number_of_bathrooms """
        return self.__number_of_bathrooms

    @number_of_bathrooms.setter
    def number_of_bathrooms(self, value):
        """Setter for private prop number_of_bathrooms"""
        if isinstance(value, int):
            self.__number_of_bathrooms = value
        else:
            raise ValueError("Invalid value specified for Number of Bathrooms: {}".format(value))

    @property
    def max_guests(self):
        """ Returns value of private property max_guests """
        return self.__max_guests

    @max_guests.setter
    def max_guests(self, value):
        """Setter for private prop max_guests"""
        if isinstance(value, int):
            self.__max_guests = value
        else:
            raise ValueError("Invalid value specified for Max Guests: {}".format(value))

    @property
    def price_per_night(self):
        """ Returns value of private property price_per_night """
        return self.__price_per_night

    @price_per_night.setter
    def price_per_night(self, value):
        """Setter for private prop price_per_night"""
        if isinstance(value, int):
            self.__price_per_night = value
        else:
            raise ValueError("Invalid value specified for Price per Night: {}".format(value))

    @property
    def latitude(self):
        """ Returns value of private property latitude """
        return self.__latitude

    @latitude.setter
    def latitude(self, value):
        """Setter for private prop latitude"""
        if isinstance(value, float):
            self.__latitude = value
        else:
            raise ValueError("Invalid value specified for Latitude: {}".format(value))

    @property
    def longitude(self):
        """ Returns value of private property longitude """
        return self.__longitude

    @longitude.setter
    def longitude(self, value):
        """Setter for private prop longitude"""
        if isinstance(value, float):
            self.__longitude = value
        else:
            raise ValueError("Invalid value specified for Longitude: {}".format(value))

    # --- Static methods ---
    # TODO:


class Amenity(Base):
    """Representation of amenity """

    datetime_format = "%Y-%m-%dT%H:%M:%S.%f"

    # Class attrib defaults
    id = None
    created_at = None
    updated_at = None
    __name = ""

    # Class attrib defaults
    __tablename__ = 'amenities'
    id = Column(String(60), nullable=False, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now())
    __name = Column("name", String(128), nullable=False)
    places = relationship("Place", secondary=place_amenity, back_populates = 'amenities')

    # constructor
    def __init__(self, *args, **kwargs):
        """ constructor """
        # Set object instance defaults
        self.id = str(uuid.uuid4())

        # Note that setattr will call the setters for attribs in the list
        if kwargs:
            for key, value in kwargs.items():
                if key in ["name"]:
                    setattr(self, key, value)

    # --- Getters and Setters ---
    @property
    def name(self):
        """Getter for private prop name"""
        return self.__name

    @name.setter
    def name(self, value):
        """Setter for private prop name"""

        # ensure that the value is not spaces-only and is alphabets + spaces only
        is_valid_name = len(value.strip()) > 0 and re.search("^[a-zA-Z ]+$", value)
        if is_valid_name:
            self.__name = value
        else:
            raise ValueError("Invalid amenity name specified: {}".format(value))

    # --- Static methods ---
    # TODO:
