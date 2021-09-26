import csv
from random import randrange
from sqlalchemy import and_
import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from config.create_app import get_session
from models import Building

header = ['rooms', 'square_footage', 'price']
TRAIN_DATA_SIZE_PERCENTAGE = 0.85

session = get_session()
buildings = session.query(Building.rooms.label('rooms'),
                          Building.square_footage.label('square_footage'),
                          Building.price.label('price')).\
    filter(Building.offer.ilike('Prodaja')).\
    filter(Building.city.ilike('Beograd')).\
    filter(Building.type_of_estate.ilike('stan')).\
    filter(and_(Building.price.isnot(None),
                Building.rooms.isnot(None),
                Building.square_footage.isnot(None))).\
    all()

with open('predict_models/train.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)

    # write the data
    train_data_size = int(len(buildings) * TRAIN_DATA_SIZE_PERCENTAGE)
    for i in range(0, train_data_size):
        row = randrange(len(buildings))
        writer.writerow(buildings.pop(row))

with open('predict_models/test.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)

    # write the data
    for data in buildings:
        writer.writerow(data)
