from random import randint
import asyncio


async def download(code):
    wait_time = randint(1, 3)
    print('downloading {} will take {} second(s)'.format(code, wait_time))
    await asyncio.sleep(wait_time)  # I/O, context will switch to main function
    print('downloaded {}'.format(code))


# download(code) is the same
async def main():
    con_limit = 10
    dltasks = set()
    for i in range(90):
        if len(dltasks) >= con_limit:
            # Wait for some download to finish before adding a new one
            _done, dltasks = await asyncio.wait(dltasks, return_when=asyncio.FIRST_COMPLETED)
        dltasks.add(asyncio.create_task(download(i)))
    # Wait for the remaining downloads to finish
    await asyncio.wait(dltasks)

if __name__ == '__main__':
    asyncio.run(main())
