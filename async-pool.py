from random import randint
import asyncio
from asyncio_pool import AioPool


async def download(code):
    wait_time = randint(1, 3)
    print('downloading {} will take {} second(s)'.format(code, wait_time))
    await asyncio.sleep(wait_time)  # I/O, context will switch to main function
    print('downloaded {}'.format(code))


# download(code) is the same
async def main():
    pool = AioPool(size=10)
    await pool.map(download, range(90))

if __name__ == '__main__':
    asyncio.run(main())
