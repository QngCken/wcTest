#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'QngCken'

'''ORM - Object Relation Map 对象关系映射
    本地数据连接数据库'''

import asyncio, logging
import aiomysql


async def create_pool(loop,**kw):   #aiomysql支持数据库异步连接
    logging.info('Create database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host = kw.get('host', 'localhost'),
        port = kw.get('port', 3306),
        user = kw['user'],
        password = kw['password'],
        db = kw['db'],
        charset = kw.get('charset', 'utf8'),
        autocommit = kw.get('autocommit', True),
        maxsize = kw.get('maxsize', 10),
        minsize = kw.get('minsize', 1),
        loop = loop
    )

async def select(sql, args, size=None): #数据库查询数据
    logging.info('SQL: %s' % sql, args)
    global __pool
    with (await __pool) as conn:
        cur = await conn.cursor(aiomysql.DictCursor)
        await cur.execute(sql.replace('?', '%s'), args or ())
        if size:
            rs = await cur.fetchmany(size)
        else:
            rs = await cur.fetchall()
        await cur.close()
        logging.info('rows returned: %s' % len(rs))
        return rs

async def execute(sql, args, autocommit=True):  #数据库插入/更新/删除数据
    logging.info('SQL: %s' % sql, args)
    with (await __pool) as conn:
        if not autocommit:
            await conn.begin()
        try:
            cur = await conn.cursor()
            await cur.execute(sql.replace('?', '%s'), args)
            affected = cur.rowcount
            await cur.close()
            if not autocommit:
                await conn.commit()
        except BaseException:
            if not autocommit:
                await conn.rollback()
            raise
        return affected

def create_args_string(num):    #格式化sql参数占位符
    L = []
    for _ in range(num):
        L.append('?')
    return ', '.join(L)


class Field(object):    #定义域，作为数据库单个表格栏/键的属性基类
    def __init__(self, name, column_type, primary_key, default):
        self.name = name                #键名/表格列名称
        self.column_type = column_type  #值数据类型
        self.primary_key = primary_key  #主键？
        self.default = default          #默认值
    def __str__(self):
        return '<%s, %s, %s>' % (self.__class__.__name__, self.column_type, self.name)

class StringField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)

class BooleanField(Field):
    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)

class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)

class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)

class TextField(Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)


class ModelMetaclass(type): #定义Model元类，在表格类创建时自动映射其属性

    def __new__(cls, name, bases, attrs):   #cls元类名，name定义类名，bases基类名，attrs定义类属性
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        tableName = attrs.get('__table__', None) or name    #没有表格名__table__属性则以类名处理
        logging.info('Found model: %s (table: %s).' % (name, tableName))
        mappings = dict()   #创建映射表
        fields = []         #创建普通栏
        primaryKey = None   #初始化主键
        for k, v in attrs.items():
            if isinstance(v, Field):    #找到表格列栏属性
                logging.info('  Found mapping: %s ==> %s.' % (k, v))
                mappings[k] = v         #添加（键：SomeField）映射
                if v.primary_key:       #查询主键
                    if primaryKey:      #如果已有主键，报错
                        raise RuntimeError('Duplicate primary key for field: %s.' % k)
                    primaryKey = k      #添加主键
                else:
                    fields.append(k)    #不是主键，添加为普通栏/列
        if not primaryKey:              #若没有发现主键，报错
            raise RuntimeError('Primary key not found.')
        for k in mappings.keys():       #数据库映射完毕，删除相应类属性
            attrs.pop(k)
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))    #将普通栏名格式化为sql参数
        attrs['__mappings__'] = mappings        #添加表格的键属性映射关系
        attrs['__table__'] = tableName          #添加表格名称映射
        attrs['__primary_key__'] = primaryKey   #添加主键映射
        attrs['__fields__'] = fields            #添加普通键映射
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)                         #获取列属性键名，没有则指定为映射键名
        #添加 查询 / 插入 / 更新 / 删除 sql格式化语句
        return type.__new__(cls, name, bases, attrs)    #返回新的构建类


class Model(dict, metaclass=ModelMetaclass):    #定义自构建模型
    def __init__(self, **kw):
        super().__init__(**kw)      #字典键值对
    
    def __getattr__(self, key):     #获取d[k]方法
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)
    
    def __setattr__(self, key, value):  #设置d[k]=v方法
        self[key] = value
    
    def getValue(self, key):    #查询d[k]方法
        return getattr(self, key, None)
    
    def getValueOrDefault(self, key):   #查询k的值，没有则获取默认值并设置
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('Using default value for %s: %s' % (key, str(value)))
                setattr(self, key, value)
        return value
    
    @classmethod        #定义类方法，不同于 staticmethod 和实例方法，直接通过类名调用
    async def findAll(cls, where=None, args=None, **kw):
        ' find objects by where clause. '
        sql = [cls.__select__]          #以列表形式获取查询格式化语句
        if where:                       #有指定范围则添加范围指令和参数
            sql.append('where')
            sql.append(where)
        if args is None:                #指定键参数
            args = []
        orderBy = kw.get('orderBy', None)   #查找排序指令
        if orderBy:                     #有则添加排序指令和参数
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit', None)   #查找分页限制指令
        if limit is not None:           #有则添加分页限制指令和参数limit=int 或 limit=(int, int)
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, (tuple, list)) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:                       #未识别类型，报错
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = await select(' '.join(sql), args)  #查询数据库
        return [cls(**r) for r in rs]   #返回数据映射类列表

    @classmethod        #类方法，类调用，用于向数据库查询
    async def findNumber(cls, selectField, where=None, args=None):
        ' find number by select and where. '
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    @classmethod        #类方法，类调用，用于向数据库查询
    async def find(cls, pk):    #根据主键查询某项数据
        ' find object by primary key. '
        rs = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    @classmethod        #模糊搜索，where=搜索关键字: "key like ?" ，like=[模糊项]，一次只能查询一项
    async def search(cls, where=None, like=None, **kw):
        args = []           #缺省查询关键字时，函数同为为findAll
        if like:
            for l in like:
                args.append('%' + l.replace('[', '[[]').replace('%', '[%]').replace('_', '[_]') + '%')
        return await cls.findAll(where, args, **kw)

    async def save(self):       #自身向数据库插入
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warn('Failed to insert record: affected rows: %s' % rows)

    async def update(self):     #自身向数据库更新
        args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = await execute(self.__update__, args)
        if rows != 1:
            logging.warn('Failed to update by primary key: affected rows: %s' % rows)

    async def remove(self):     #自身向数据库请求删除
        args = [self.getValue(self.__primary_key__)]
        rows = await execute(self.__delete__, args)
        if rows != 1:
            logging.warn('Failed to remove by primary key: affected rows: %s' % rows)



