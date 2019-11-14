import aiohttp
import asyncio
from bs4 import BeautifulSoup
import csv
import httpx
import os


class Zipcode:
    def __init__(self, *, values, keys, name):
        self.__dict__ = dict(zip(keys, values))
        self.name = name

    def __repr__(self):
        return self.name

# def async_fetch(*, list_of_objects, concurrency_limit, tag_type, dict_to_check):

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import httpx
import os


async def fetch(url):
    SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY', '')
    SCRAPERAPI_URL = 'http://api.scraperapi.com'
    params = {
        'api_key': SCRAPER_API_KEY,
        'url': url
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(SCRAPERAPI_URL, timeout=60, params=params)
        return r.text


async def get_serps_response(paginated_urls):
    async with aiohttp.ClientSession():
        soups = []
        for serp_url_block in paginated_urls:
            responses = await asyncio.gather(
                *[fetch(url) for url in serp_url_block])
            soups.extend([BeautifulSoup(resp, 'html.parser') for resp in responses])
        return soups


if __name__ == "__main__":
    with open('/Users/work/Dropbox/Projects/Working Data/flipfind/zillow_urls_florida.csv', encoding='utf-8-sig') as f:
        data = list(csv.reader(f))
        zipcodes = [Zipcode(values=row,
                            keys=data[0],
                            name=f'{row[2]}-{row[0]}')
                    for i, row in enumerate(data[1:])]

    import pdb; pdb.set_trace()

    paginated_url_blocks = [["https://www.zillow.com/delray-beach-FL-33446/sold/house_type/?searchQueryState={'mapZoom': 13, 'filterState': {'isForSaleByAgent': {'value': False}, 'isForSaleByOwner': {'value': False}, 'isNewConstruction': {'value': False}, 'isForSaleForeclosure': {'value': False}, 'isComingSoon': {'value': False}, 'isAuction': {'value': False}, 'isPreMarketForeclosure': {'value': False}, 'isPreMarketPreForeclosure': {'value': False}, 'isMakeMeMove': {'value': False}, 'isRecentlySold': {'value': True}, 'isCondo': {'value': False}, 'isMultiFamily': {'value': False}, 'isManufactured': {'value': False}, 'isLotLand': {'value': False}, 'isTownhouse': {'value': False}, 'isApartment': {'value': False}, 'price': {'min': 2000001}}, 'isListVisible': True, 'isMapVisible': False, 'mapBounds': {'west': -80.229613, 'east': -80.146376, 'south': 26.423853, 'north': 26.483953}, 'regionSelection': [{'regionId': 72612, 'regionType': 7}], 'pagination': {'currentPage': 1}}"]]

    soups = []

    soups.extend(asyncio.run(get_serps_response(paginated_url_blocks)))
    print(soups)