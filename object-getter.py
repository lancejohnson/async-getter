import aiohttp
import asyncio
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt
import httpx
import os
import pickle


def async_fetch(*, object_list, con_limit, tag_type, dict_to_check, out_file):
    '''
    Objects must have url parameter to work
    '''
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

    async def gather_object_blocks(object_list):
        object_blocks = [object_list[i:i + con_limit]
                         for i in range(0, len(object_list), con_limit)]
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

    def save_object(obj, filename):
        with open(filename, 'wb') as output:  # Overwrites any existing file.
            pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

    asyncio.run(gather_object_blocks(object_list))
    save_object(object_list, out_file)
