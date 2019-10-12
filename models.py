#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'数据库表格-数据映射模型'
__author__ = 'QngCken'

from uuid import uuid4
from time import time
from orm import Model, StringField, BooleanField, TextField#, FloatField, IntegerField

def next_uuid():  #自动生成uuid通识符
    return '%s' % str(uuid4())

def next_id():
    return '0%015d%s0' % (int(time() * 1000), uuid4().hex)

class Simul(Model):
    __table__ = 'sims'
    
    uuid = StringField(primary_key=True, default=next_uuid, ddl='varchar(50)')
    status = BooleanField()


class Device(Model):
    __table__ = 'devices'
    # 坑位
    uuid = StringField(primary_key=True, default=next_uuid, ddl='varchar(50)')
    parid = StringField()
    status = BooleanField()

class Toilet(Model):
    __table__ = 'toilets'
    # 一楼东卫生间
    selfid = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    sex = StringField(ddl='varchar(6)')    #厕所性别male, female, third
    name = StringField()                   #地点名称
    point = StringField(ddl='varchar(15)')
    parid = StringField(ddl='varchar(50)')                    #上级id

class Building(Model):
    __table__ = 'buildings'
    # 二教
    selfid = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    name = StringField()
    parid = StringField()

class Area(Model):
    __table__ = 'areas'
    # 电子科技大学（沙河校区）
    selfid = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    name = StringField()
    parid = StringField()

class Scene(Model):
    __table__ = 'scenes'

    sid = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    sname = StringField()
    # scode = StringField(ddl='varchar(50)')
    # spar = StringField()
    schd = StringField(ddl='varchar(50)')


####################################################
class Maptest(Model):
    __table__ = 'maps'

    selfid = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    name = StringField()
    parid = StringField(ddl='varchar(50)')
    # slf = StringField(ddl='varchar(50)')
    # chd = StringField(ddl='varchar(50)')
    border = TextField()











'''
    clsname(**kw) ==> ==>

    类属性
        __table__ = ...     表格名称
        __mapping__ = ...   表格映射
        __primary_key = ... 主键映射
        __fields__ = ...    副键映射
        __select__ = ...    查询格式化语句
        __insert__ = ...    插入格式化语句
        __update__ = ...    更新格式化语句
        __delete__ = ...    删除格式化语句

    实例方法
        __init__(**kw)          构建成一个字典，但是构建成功之后键值对被映射入类属性中的映射表中，这是<<重点>>
        __getattr__(key)        实现点运算查找k-v键值对，报错
        __setattr__(key)        实现点运算属性k-v赋值
        getValue(key)           获取键值，不报错
        getValueOrDefault(key)  获取键值，不存在则自动填充默认值，不报错
        save()                  提交（自身）插入，保存数据库数据
        update()                提交（自身）更新，更新数据库数据
        remove()                提交（自身）删除，删除数据库数据

    类方法
        findAll(where=None, args=None, **kw)    #查询所有数据
        ==> where 为 True 时，添加where内容及范围参数args
        ==> kw 为附加设置orderBy和limit语句
        ==> 如：findAll(where='`key1`=?, `key2`=?', args=[value1, value2], {
            orderBy='key3[ desc/asc][, key4[ desc/asc]]'，  #详见mySQL中 "order by"用法
            limit=int/(offset, limit)/[int, int]            #详见mySQL中 "limit"用法
        })
        ==> 查询正常则返回查询数据的[class实例对象]的列表，包括空列表，异常则报错

        findNumber(selectField, where=None, args=None)
        ==> selectField SQL聚合函数：'count(*)', 'count(key5)'  #函数内部已对查询结果进行重命名
        ==> where, args 用法参考findAll
        ==> 查询正常返回查询结果，异常则返回None，或报错

        find(pk)        #按主键查询一个数据
        ==> 数据存在则返回数据class实例对象，否则返回None
'''