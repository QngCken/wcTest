import orm, asyncio, aiohttp
from models import Maptest
from config import configs
from wctest import timeuse

@timeuse('search')
async def search(loop):
    await orm.create_pool(loop, **configs.db)
    s = await Maptest.search(key='`name` like ?', like=['区'])
    for i in s:
        print(i.name)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search(loop))