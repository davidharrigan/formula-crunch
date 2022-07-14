import httpx

URL = 'https://ergast.com/api/f1/{year}/drivers.json'


def scrape_drivers(year):
    url = URL.format(year=year)
    res = httpx.get(url)
    if res.status_code != 200:
        raise Exception(f'expected 200 status, got: {res.status_code}')

    payload = res.json()
    print(payload)
