from math import sqrt
import argparse
import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from config.create_app import get_session
from models import Building

PRICE_TYPE_NAMES = {
    0: 'Cheaper than 50000',
    1: 'Between 50000 and 99999',
    2: 'Between 100000 and 149999',
    3: 'Between 150000 and 199999',
    4: 'More expensive than 200000'
}

span_of_price = [0, 0, 0, 0, 0]


def sort_list(elem):
    return elem['distance']


def calculate_distance(x1, y1, x2, y2, algorithm):
    if algorithm == 0:
        return sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))
    else:
        return abs(x1 - x2) + abs(y1 - y2)


def evaluate_new_appartment():
    session = get_session()
    buildings = session.query(Building).\
        filter(Building.offer.ilike('Prodaja')).\
        filter(Building.city.ilike('Beograd')).\
        filter(Building.type_of_estate.ilike('stan')).\
        all()
    parser = argparse.ArgumentParser()
    parser.add_argument('--k', default=sqrt(len(buildings)))
    parser.add_argument('--algorithm', default=0)
    k = int(parser.parse_args().k)
    algorithm = int(parser.parse_args().algorithm)
    try:
        rooms = float(input().strip())
        square_footage = float(input().strip())
    except ValueError:
        print("Bad input parameters")
        return None
    distances = []
    for b in buildings:
        b_rooms = b.rooms if b.rooms else 0
        b_square_footage = b.square_footage if b.square_footage else 0
        b_price = b.price if b.price else -1
        distance = calculate_distance(
            b_rooms, b_square_footage, rooms, square_footage, algorithm)
        elem = {
            'price': b_price,
            'distance': distance
        }
        distances.append(elem)

    distances.sort(key=sort_list)

    for i in range(0, k-1):
        if distances[i]['price'] == -1:
            continue
        if distances[i]['price'] < 50000:
            span_of_price[0] += 1
        elif 50000 <= distances[i]['price'] < 100000:
            span_of_price[1] += 1
        elif 100000 <= distances[i]['price'] < 150000:
            span_of_price[2] += 1
        elif 150000 <= distances[i]['price'] < 200000:
            span_of_price[3] += 1
        elif distances[i]['price'] >= 200000:
            span_of_price[4] += 1

    max_value = max(span_of_price)
    max_index = span_of_price.index(max_value)

    print('Evaluate price is ' + PRICE_TYPE_NAMES[max_index])


if __name__ == '__main__':
    evaluate_new_appartment()
