import datetime
import logging
import json

import httpx
from sqlalchemy.orm import Session

from .data import write_file, get_file
from .db import create_connection
from .models import Driver

URL = 'https://ergast.com/api/f1/{year}/drivers.json'


def scrape_drivers(year, force=False):
    url = URL.format(year=year)
    filename = f'drivers/{year}.json'
    raw_file = get_file(filename)
    if raw_file and not force:
        content = json.loads(raw_file)
    else:
        logging.debug(f'{filename} does not exist yet, start scraping')
        res = httpx.get(url)
        if res.status_code != 200:
            raise Exception(f'expected 200 status, got: {res.status_code}')
        content = res.json()['MRData']['DriverTable']
        write_file(filename, json.dumps(content, indent=2))
        logging.info(f'{filename} written')

    # TODO: this will break if there's already stuff in the db
    conn = create_connection()
    with Session(conn) as session:
        for driver in content["Drivers"]:
            session.add(Driver(
                driver_id=driver["driverId"],
                driver_number=driver["permanentNumber"],
                code=driver["code"],
                given_name=driver["givenName"],
                family_name=driver["familyName"],
                birthday=datetime.date.fromisoformat(driver["dateOfBirth"]),
                nationality=driver["nationality"],
            ))
        session.commit()
