#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'QngCken'

'''Configuration
    合并override文件和default文件
    生成一维字典键值对'''

__author__ = 'Michael Liao'

import defaultConfig as d

class Dict(dict):
    '''Simple dict but support access as x.y style.'''
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key): #支持"."点运算
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

def merge(defaults, override):  #合并
    r = {}
    for k, v in defaults.items():
        if k in override:
            if isinstance(v, dict):
                r[k] = merge(v, override[k])
            else:
                r[k] = override[k]
        else:
            r[k] = v
    return r

def toDict(d):  #遍历配置信息，使其支持点运算符
    D = Dict()
    for k, v in d.items():
        D[k] = toDict(v) if isinstance(v, dict) else v
    return D

configs = d.configs

try:
    import overrideConfig as o
    configs = merge(configs, o.configs)
except ImportError:
    pass

configs = toDict(configs)
