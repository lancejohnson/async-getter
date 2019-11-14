import aiohttp
import asyncio
from bs4 import BeautifulSoup
import csv
from tenacity import retry, stop_after_attempt
import httpx
import os


class Zipcode:
    def __init__(self, *, values, keys, name):
        self.__dict__ = dict(zip(keys, values))
        self.name = name

    def __repr__(self):
        return self.name


def async_fetch(*, list_of_objects, concurrency_limit, tag_type, dict_to_check):
    @retry(stop=stop_after_attempt(5))
    async def fetch(the_object):

        SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY', '')
        SCRAPERAPI_URL = 'http://api.scraperapi.com'
        params = {
            'api_key': SCRAPER_API_KEY,
            'url': the_object.url
        }
        async with httpx.AsyncClient() as client:
            r = await client.get(SCRAPERAPI_URL, timeout=60, params=params)

            test_soup = BeautifulSoup(r.text, 'html.parser')
            if test_soup.find(tag_type, dict_to_check):
                the_object.response_text = r.text
            else:
                the_object.response_text = 'Soup test failed'
                raise ValueError(f'Soup test failed for {the_object.url}')

            # TODO write object to CSV when it passes the soup test

    async def gather_object_blocks(list_of_objects):
        object_blocks = [list_of_objects[i:i + concurrency_limit]
                         for i in range(0, len(list_of_objects), concurrency_limit)]
        async with aiohttp.ClientSession():
            for sub_block in object_blocks:
                try:
                    await asyncio.gather(
                        *[fetch(the_object) for the_object in sub_block])
                    # TODO Add try/except to each object, so if it fails, it'll
                    # continue to the next object rather than hoping all the other
                    # elements have finished.
                    # Video: https://www.loom.com/share/165a7f636eb9413a9b2e5a3f9e1d1bb5
                    # Gist: https://gist.github.com/lancejohnson/beb3107ace8516d89149dc1a23fc9d77
                except Exception as e:
                    print(f'Continuing. The problem was {e}')
                    continue
    asyncio.run(gather_object_blocks(list_of_objects))


if __name__ == "__main__":
    with open('/Users/work/Dropbox/Projects/Working Data/flipfind/zillow_urls_florida.csv', encoding='utf-8-sig') as f:
        data = list(csv.reader(f))
        zipcodes = [Zipcode(values=row,
                            keys=data[0],
                            name=f'{row[2]}-{row[0]}')
                    for i, row in enumerate(data[1:])]

    tag_type = 'script'
    dict_check = {'data-zrr-shared-data-key': 'mobileSearchPageStore'}
    async_fetch(
        list_of_objects=zipcodes[:2], concurrency_limit=10, tag_type=tag_type, dict_to_check=dict_check)
    import pdb
    pdb.set_trace()
