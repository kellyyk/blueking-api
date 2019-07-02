# -*- coding: utf-8 -*-
"""
Copyright © 2012-2018 Tencent BlueKing. All Rights Reserved. 蓝鲸智云 版权所有
"""


def str_bool(value):
    if isinstance(value, basestring):
        value = value.strip()
        if value.lower() in ("0", "false"):
            return False
    return bool(value)


class FancyDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError, k:
            raise AttributeError(k)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError(k)


def smart_lower(value):
    result = [value[0].lower()]
    for c in value[1:]:
        if c >= 'A' and c <= 'Z':
            result.append('_')
        result.append(c.lower())
    return ''.join(result)


def smart_str(s, encoding='utf-8'):
    if isinstance(s, unicode):
        return s.encode(encoding)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', 'ignore').encode(encoding, 'ignore')
    else:
        return str(s)


def smart_unicode(s, encoding='utf-8'):
    if isinstance(s, unicode):
        return s
    return s.decode(encoding, 'ignore')
