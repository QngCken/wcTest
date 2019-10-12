import orm, asyncio, aiohttp
from models import Maptest
from config import configs
from wctest import timeuse

async def add(loop, **kw):
    await orm.create_pool(loop, **configs.db)
    pid = 'None'
    if kw['parid'] !='None':
        ps = await Maptest.findAll(where='name=?', args=(kw['parid'],))
        for p in ps:
            pid = p.get('selfid', 'error')
    m = Maptest(name=kw['name'], parid=pid, border=kw['border'])
    await m.save()

def mtest():
    from simulateMap import areaMap
    loop = asyncio.get_event_loop()
    for kw in areaMap:
        loop.run_until_complete(add(loop, **kw))

# if __name__ == "__main__":
#     mtest()
########################################################
def parsexy(xystr:str):
    xys = xystr.split('&')
    return [xy.split(',') for xy in xys]

def PNpoly(x, y, bdr:list):
    c = False
    for n in range(len(bdr)):
        y1 = eval(bdr[n][1])
        y0 = eval(bdr[n-1][1])
        if (y>y1) != (y>y0):
            x1 = eval(bdr[n][0])
            x0 = eval(bdr[n-1][0])
            if x < (x0 - x1) * (y - y1) / (y0 - y1) + x1:
                c = not c
    return c
# @timeuse('获取位置')
async def pos(x, y, p="None"): # 从已知p位置向下寻找
    pid = p
    pos = []
    while True:
        found = False
        rs = await Maptest.findAll(where='`parid`=?', args=(pid,))
        if len(rs) == 0:
            break
        for r in rs:
            if PNpoly(x, y, parsexy(r['border'])):
                pid = r['selfid']
                pos.append(r['name'])
                found = True
                break
        if not found:
            break
    return pos

async def ptest(loop):
    await orm.create_pool(loop, **configs.db)
    return await asyncio.ensure_future(pos(510, 350))
    

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    r = loop.run_until_complete(ptest(loop))
    print(r)