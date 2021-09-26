import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

from config.create_app import Base, engine, get_session
from models import Building


def extract_data_from_page(soup, type_of_estate):
    state = ''
    city = ''
    city_part = ''
    parking = ''
    heating = ''
    registration = ''
    rooms = ''
    floors = ''
    square_footage = ''
    land_area = ''
    offer = ''
    construction_year = ''
    bathrooms = ''
    additional_information = ''

    location_list = soup.find('div', class_='property__location')
    if location_list:
        location_list = location_list.find('ul').find_all('li')
        if len(location_list) > 0:
            state = location_list[0].text
        if len(location_list) > 2:
            city = location_list[2].text
        if len(location_list) > 3:
            city_part = location_list[3].text
    header_list = soup.find('div', class_='property__main-details')
    if not header_list:
        return None
    header_list = header_list.find('ul').find_all('li')
    for hl in header_list:
        if hl.find('span').find('span') and \
                hl.find('span').find('span').text == 'Parking:':
            parking = True if hl.find('span').text.split(':')[-1].\
                strip().replace('-', '') == 'Da' else False
        if hl.find('span').find('span') and \
                hl.find('span').find('span').text == 'Grejanje:':
            heating = hl.find('span').text.split(':')[-1].\
                strip().replace('-', '')
        if hl.find('span').find('span') and \
                hl.find('span').find('span').text == 'Uknjiženo:':
            registration = True if hl.find('span').text.split(':')[-1].\
                strip().replace('-', '') == 'Da' else False
        if hl.find('span').find('span') and \
                hl.find('span').find('span').text == 'Sobe:':
            rooms = hl.find('span').text.split(':')[-1].\
                strip().replace('-', '')
        if hl.find('span').find('span') and \
                hl.find('span').find('span').text == 'Sprat:':
            floors = hl.find('span').text.split(':')[-1].\
                strip().replace('-', '')
        if hl.find('span').find('span') and \
                hl.find('span').find('span').text == 'Kvadratura:':
            square_footage = hl.find('span').text.split(':')[-1].\
                strip().replace(' m²', '')
            if '-' in square_footage or 'ar' in square_footage:
                return None
        if hl.find('span').find('span') and \
                hl.find('span').find('span').text == 'Površina zemljišta:':
            land_area = hl.find('span').text.split(':')[-1].\
                strip().replace(' ar', '').replace('-', '')
            if ' m²' in land_area:
                land_area = float(land_area.replace(' m²', '')) / 100

    details = soup.find('div', class_='property__amenities').\
        find('ul').find_all('li')
    if len(soup.find_all('div', class_='property__amenities')) > 1 and \
            soup.find_all('div', class_='property__amenities')[1].\
            find('h3').text == 'Dodatna opremljenost':
        additional_info_list = \
            soup.find_all('div', class_='property__amenities')[1].\
            find('ul').find_all('li')
    else:
        additional_info_list = []

    for detail in details:
        if 'Transakcija:' in detail.text:
            offer = detail.find('strong').text.strip()
        if 'Godina izgradnje:' in detail.text:
            construction_year = detail.find('strong').text.strip()
        if 'Broj kupatila:' in detail.text:
            bathrooms = detail.find('strong').text.strip()
            # on some pages bathroom is float
            if '.' in bathrooms:
                bathrooms = bathrooms.split('.')[0]

    for info in additional_info_list:
        additional_information += info.text.strip() + ' - '
    additional_information = additional_information[:-3]

    if not isinstance(parking, bool):
        parking = None

    if not isinstance(registration, bool):
        registration = None

    price = soup.find('div', class_='stickyBox__price-size').\
        find('h4', class_='stickyBox__price').text
    if 'Po dogovoru' in price:
        price = None
    else:
        price = price.split('EUR')
        if len(price) > 1:
            price = price[0].replace(' ', '')
        else:
            price = None

    building = Building(
        type_of_estate=type_of_estate,
        state=state if state else None,
        city=city if city else None,
        city_part=city_part if city_part else None,
        parking=parking,
        heating=heating if heating else None,
        registration=registration,
        rooms=rooms if rooms else None,
        floors=floors if floors else None,
        square_footage=square_footage if square_footage else None,
        land_area=land_area if land_area else None,
        offer=offer,
        construction_year=construction_year if construction_year else None,
        bathrooms=bathrooms if bathrooms else None,
        price=price,
        additional_information=additional_information if additional_information
        else None
        )
    return building


def scrape_appartments(web_session, db_session, base_url, apartments_url):
    page = 1
    while True:
        apartments_page = web_session.get(apartments_url.format(page))
        main_soup = BeautifulSoup(apartments_page.content, 'html.parser')
        apartments = main_soup.find_all("div", attrs={"class": "row offer"})
        if not apartments:
            break
        for a in apartments:
            if not a.find('a').get('href'):
                continue
            apartment_url = base_url + a.find('a').get('href')
            apartment_page = web_session.get(apartment_url)
            apartment_soup = BeautifulSoup(apartment_page.content,
                                           'html.parser')
            if not apartment_soup:
                continue
            building = extract_data_from_page(apartment_soup, 'stan')
            if building:
                db_session.add(building)
        if page % 5 == 0:
            db_session.commit()
        if page % 100 == 0:
            time.sleep(60)
        page += 1
    db_session.commit()


def scrape_houses(web_session, db_session, base_url, houses_url):
    page = 1
    while True:
        houses_page = web_session.get(houses_url.format(page))
        main_soup = BeautifulSoup(houses_page.content, 'html.parser')
        houses = main_soup.find_all("div", attrs={"class": "row offer"})
        if not houses:
            break
        for h in houses:
            if not h.find('a').get('href'):
                continue
            house_url = base_url + h.find('a').get('href')
            house_page = web_session.get(house_url)
            house_soup = BeautifulSoup(house_page.content, 'html.parser')
            if not house_soup:
                continue
            building = extract_data_from_page(house_soup, 'kuća')
            if building:
                db_session.add(building)
        if page % 5 == 0:
            db_session.commit()
        if page % 100 == 0:
            time.sleep(60)
        page += 1

    db_session.commit()


def main():
    Base.metadata.create_all(engine)
    db_session = get_session()
    base_url = 'https://www.nekretnine.rs'

    houses_url = base_url + '/stambeni-objekti/kuce/lista/' \
                            'po-stranici/10/stranica/{}'

    apartments_for_sale_url = \
        base_url + '/stambeni-objekti/stanovi/izdavanje-prodaja/'\
                   'prodaja/lista/po-stranici/10/stranica/{}'
    apartments_for_rent_url = \
        base_url + '/stambeni-objekti/stanovi/izdavanje-prodaja/izdavanje/' \
                   'lista/po-stranici/10/stranica/{}'

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2)"
                      " AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/64.0.3282.140"
                      " Safari/537.36"}

    web_session = requests.Session()
    web_session.headers.update(headers)

    print(datetime.now())
    # scrapping apartments
    scrape_appartments(
        web_session, db_session, base_url, apartments_for_sale_url)
    time.sleep(60)
    scrape_appartments(
        web_session, db_session, base_url, apartments_for_rent_url)
    time.sleep(60)

    # scrapping houses
    scrape_houses(
        web_session, db_session, base_url, houses_url)

    db_session.commit()
    db_session.close()
    print(datetime.now())


if __name__ == '__main__':
    main()

