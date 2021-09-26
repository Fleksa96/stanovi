from sqlalchemy import Column, Integer, String, Boolean, Float
import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from config.create_app import Base


class Building(Base):
    __tablename__ = 'buildings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type_of_estate = Column(String, nullable=False)
    offer = Column(String, nullable=False)
    state = Column(String, nullable=True)
    city = Column(String, nullable=True)
    city_part = Column(String, nullable=True)
    square_footage = Column(Float, nullable=True)
    construction_year = Column(Integer, nullable=True)
    land_area = Column(Float, nullable=True)
    floors = Column(String, nullable=True)
    registration = Column(Boolean, nullable=True)
    heating = Column(String, nullable=True)
    rooms = Column(Float, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    parking = Column(Boolean, nullable=True)
    additional_information = Column(String, nullable=True)
    price = Column(Integer, nullable=True)

    def __init__(self, type_of_estate, offer, state,  city, city_part,
                 square_footage, construction_year, land_area, floors,
                 registration, heating, rooms, bathrooms, parking,
                 additional_information, price):
        self.type_of_estate = type_of_estate
        self.offer = offer
        self.state = state
        self.city = city
        self.city_part = city_part
        self.square_footage = square_footage
        self.construction_year = construction_year
        self.land_area = land_area
        self.floors = floors
        self.registration = registration
        self.heating = heating
        self.rooms = rooms
        self.bathrooms = bathrooms
        self.parking = parking
        self.additional_information = additional_information
        self.price = price
