import aiohttp
import asyncio
import csv
import httpx
import os


class Zipcode:
    def __init__(self, *, values, keys, name):
        self.__dict__ = dict(zip(keys, values))
        self.name = name

    def __repr__(self):
        return self.name


def async_fetch(*, list_of_objects, concurrency_limit, tag_type, dict_to_check):
    async def fetch(the_object):

        SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY', '')
        SCRAPERAPI_URL = 'http://api.scraperapi.com'
        params = {
            'api_key': SCRAPER_API_KEY,
            'url': the_object.url
        }
        async with httpx.AsyncClient() as client:
            r = await client.get(SCRAPERAPI_URL, timeout=60, params=params)
            the_object.response_text = r.text

    async def gather_object_blocks(list_of_objects):
        object_blocks = [list_of_objects[i:i + concurrency_limit]
                         for i in range(0, len(list_of_objects), concurrency_limit)]
        async with aiohttp.ClientSession():
            for sub_block in object_blocks:
                await asyncio.gather(
                    *[fetch(the_object) for the_object in sub_block])

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
