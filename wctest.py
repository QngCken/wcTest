#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import orm, asyncio, aiohttp, json
import functools
from time import time, sleep
from threading import Thread
from models import Simul
from config import configs

###耗时统计 装饰器
def timeuse(text='', flag=1):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kw):
            ts = time()
            r = await func(*args, **kw)
            te = time()
            if int(te*1000)%flag == 0:
                print(text + ':', te-ts)
            return r
        return wrapper
    return decorator


async def add(loop):
    await orm.create_pool(loop=loop, **configs.db)
    d = Simul(status=bool(int(time()*1000)%2))
    await d.save()
    print('add: ', d, type(d))

async def fetch(loop, limit=None):
    await orm.create_pool(loop=loop, **configs.db)
    ds = await Simul.findAll(limit=limit)
    with open('json.txt', 'w') as f:
        json.dump(ds, f)
    # for d in ds:
    #     print('fnd: ', d, str(isinstance(d, dict)))

async def count(loop):
    await orm.create_pool(loop=loop, **configs.db)
    c = await Simul.findNumber('count(uuid)')
    print('nmb: ', c, type(c))

# if __name__ == "__main__":
#     for i in range(1):
#         loop = asyncio.get_event_loop()
#         loop.run_until_complete(asyncio.wait([fetch(loop, limit=(0, 5))]))
#         print('Test finished')

######################################################################
####    上面测试数据库通路，下面模拟设备数据
######################################################################


@timeuse('', 5)
async def runwc(sn, url, data, headers):
    async with sn.post(url, data=json.dumps(data), headers=headers) as r:
        if r.status != 200:
            raise ValueError

async def simulate(loop, step = 50):
    await orm.create_pool(loop, **configs.db)
    t = time()
    c = await Simul.findNumber('count(uuid)') - 800
    print('fdn: ', c, time()-t)
    te = 0
    for i in range(0, c - 1, step):
        ts = time()
        ds = await Simul.findAll(limit=(i, step))
        te += time() - ts
        for d in ds:
            yield d
    print('fda: ', step, te)

##################################################################
#########   串行post

# async def work(loop, step):
#     headers = {'Content-Type': 'application/json;charset=utf-8'}
#     url = 'http://www.adokii.com/deviceTest.php'
#     async with aiohttp.ClientSession() as sn:
#         ts = time()
#         te = 0
#         async for data in simulate(loop, step):
#             t = time()
#             await runwc(sn, url, data, headers=headers)
#             te += time() - t
#         print('snd: ', te, '\nEnd: ', time()-ts)

# def main():
#     # for i in [5, 10, 20, 50, 100, 200, 500]:
#     for i in [10]:
#         loop = asyncio.get_event_loop()
#         loop.run_until_complete(asyncio.wait([work(loop, i)]))

# if __name__ == "__main__":
#     main()

###################################################################
########    集体异步并发post

# async def work(loop, data):
#     headers = {'Content-Type': 'application/json;charset=utf-8'}
#     url = 'http://www.adokii.com/deviceTest.php'
#     async with aiohttp.ClientSession() as sn:
#         await runwc(sn, url, data, headers=headers)

# def main():
#     for i in [20]:#range(10, 301, 10):
#         loop = asyncio.get_event_loop()
#         loop.run_until_complete(asyncio.wait([fetch(loop, limit=(i, i))]))
#         with open('json.txt', 'r') as f:
#             data = json.load(f)
#         loop = asyncio.get_event_loop()
#         t = time()
#         loop.run_until_complete(asyncio.wait([work(loop, d) for d in data]))
#         print('Num', i, 'ended in', time()-t)

# if __name__ == "__main__":
#     main()


###################################################################
########    逐个异步并发post

# async def work(data):
#     headers = {'Content-Type': 'application/json;charset=utf-8'}
#     url = 'http://www.adokii.com/deviceTest.php'
#     async with aiohttp.ClientSession() as sn:
#         t = time()
#         await runwc(sn, url, data, headers=headers)
#         print('snd: ', time()-t)

# async def crt(wloop):
#     async for data in simulate(wloop, 10):
#         asyncio.run_coroutine_threadsafe(work(data), wloop)

# def sec(wloop):
#     asyncio.set_event_loop(wloop)
#     wloop.run_forever()                            #异步任务线程一直运行

# def main():
#     wrkloop = asyncio.new_event_loop()  
#     wk = Thread(target=sec, args=(wrkloop,))        #创建任务线程，发送数据信息
#     wk.start()      #启动线程，即运行异步事件循环
#     simloop = asyncio.new_event_loop()               #设备线程，添加数据信息
#     simloop.run_until_complete(crt(wrkloop))

# if __name__ == "__main__":
#     # for i in [5, 10, 20, 50, 100, 200, 500]:
#     main()

############################################查询
# @timeuse('find from keys')
# async def querydb(loop):
#     await orm.create_pool(loop, **configs.db)
#     return await Simul.findAll('status=?', [0])

# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     ss = loop.run_until_complete(querydb(loop))
#     sleep(5)
#     for s in ss:
#         print(s)

