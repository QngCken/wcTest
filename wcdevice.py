import orm, asyncio, aiohttp, json, random
from models import Device, Toilet, Building, Area
from config import configs
from wctest import timeuse
from maptest import pos
import data

####### 添加数据  #######

async def addA():
    a1 = Area(name='电子科技大学（沙河校区）', parid='xxx')
    a2 = Area(name='电子科技大学（清水河校区）', parid='xxx')
    await a1.save()
    await a2.save()
    return a1, a2

async def addB(n, p):
    b = Building(name=n, parid=p)
    await b.save()
    return b

async def addT(n, s, pnt, pid):
    t = Toilet(name=n, sex=s, point=pnt, parid=pid)
    await t.save()
    return t

async def addD(p, s):
    d = Device(parid=p, status=s)
    await d.save()
    return d
@timeuse('生成数据')
async def add():
    areas = asyncio.ensure_future(addA())
    await areas
    #生成了两大校区(2)
    f = [0]
    for a in areas.result():
        builds = await asyncio.gather(*[addB(i, a.selfid) for i in data.bs[f[0]]])
        #生成了各校区建筑楼栋(6+6) a1沙河, a2清水河
        f.append(0)
        for b in builds:
            toilets = await asyncio.gather(*[addT(n, s, data.tp[f[0]][f[1]][i%4], b.selfid) for i, (n, s) in enumerate(data.ts)])
            #生成了各建筑下卫生间(5*2*2*12)
            for t in toilets:
                await asyncio.wait([addD(t.selfid, 0) for _ in range(6)])
                #生成了各卫生间里的6个坑位(6*5*2*2*12)
            f[1] += 1
        f.pop()
        f[0] += 1

async def getN(tid):
    return await Device.findNumber('count(uuid)', 'parid=? and status=?', [tid, 0])
@timeuse('获取附近可用厕所')
async def getNa(tid):
    ct = await Toilet.find(tid)
    ts = await Toilet.findAll('`parid`=?', [ct.parid])
    tasks = []
    for t in ts:
        tasks.append(id2dir(tid=t.selfid))
        tasks.append(getN(t.selfid))
    rs = await asyncio.gather(*tasks)
    i = False
    a = []
    for r in rs:
        a.append(r)
        if i:
            print(a)
            a.clear()
        i = not i
@timeuse('获取所有设备号')
async def getD():
    devices = await Device.findAll()
    with open('uuids.txt', 'w') as f:
        for d in devices:
            f.write(d.uuid + '\n')

@timeuse('查询厕所位置')
async def id2dir(uuid=None, tid=None):
    if uuid:
        id = (await Device.find(uuid)).parid
    elif tid:
        id = tid
    else:
        return
    t = await Toilet.find(id)
    x, y = t.point.split(',')
    r = await pos(eval(x), eval(y))
    r.append(t.name)
    r.append(t.sex)
    return r
    # *(map(eval, t.dir.split(',')))

async def run(sn, u):
    ti = 30     # 时间基数
    running = True
    url = 'http://www.adokii.com/deviceTest.php'
    h = {'Content-Type': 'application/json;charset=utf-8'}
    data = {'uuid': u, 'status': 0}
    await asyncio.sleep(round(random.random()*ti, 2))
    while running:
        sorb = random.randint(0,1)
        usetime = random.randint(5*ti, 10*ti) if sorb else random.randint(int(0.5*ti), 1*ti)
        # smltime = random.randint(int(0.5*ti), 1*ti) # 小便
        # bigtime = random.randint(5*ti, 10*ti)       # 大便
        waitime = random.randint(0*ti, 30*ti)       # 空闲

        for i in [1, 0]:
            data['status'] = i
            r = await sn.post(url, data=json.dumps(data), headers=h)
            if r.status != 200:
                print('Device worked error:', u)
                running = False
                break
            if i:
                print(u[:4], 'used')
                await asyncio.sleep(usetime)
            else:
                print(u[0:4], 'unused')
                await asyncio.sleep(waitime)

async def runAll(sn):
    with open('uuids.txt', 'r') as f:
        while True:
            u = f.readline()[:-1]
            if u:
                asyncio.ensure_future(run(sn, u))
            else:
                break

async def work(loop):
    async with aiohttp.ClientSession() as sn:
        loop.create_task(runAll(sn))
        while True:
            await asyncio.sleep(100)

async def main(loop):
    await orm.create_pool(loop, **configs.db)
    # await getD()
    # print(await id2dir(uuid='04b856c9-0b5c-45ff-b34a-2d0c692ba0e1'))
    # await work(loop)
    # await add()
    await asyncio.gather(
        getNa(tid='0001570879829234feefe27357f444649ae95fc9ffb56f990'),
        getNa(tid='0001570879832000ef3191f31f6c48c4bb14501d5cdbb9250'),
        getNa(tid='00015708798319991766e83810b24e84b1078d58d3516b5b0'),
        getNa(tid='0001570879825057ff3320fe574f411db91220362b8de1040'),
        getNa(tid='0001570879823698e262b6d2520b4262b7a8953fb49287100'),
        getNa(tid='0001570879834737ae2723c4711c4c03bbddafcba93a73290'),
        getNa(tid='00015708798236981df7af1b2a6b460eaf1adb481c5ddd620'),
        getNa(tid='0001570879825057dbe83e6a33904f8fa51133bd553413ff0'),
        getNa(tid='0001570879826416040b159ac4824e1a8bb99be7b9fda2aa0'),
        getNa(tid='0001570879826417329915e72b1e4ab7a7bd26f732bdb1e80'),
        getNa(tid='000157087982641793d1634083114b1891bc56a386aa5ac80'),
        getNa(tid='000157087982787528ee11cb68c443adad8fbb315d49181f0'),
        getNa(tid='000157087982787684fd933a41434ae6a90a28bfb9bdd1690'),
    )
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))