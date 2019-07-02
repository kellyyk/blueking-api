# -*- coding: utf-8 -*-
"""
Copyright © 2012-2018 Tencent BlueKing. All Rights Reserved. 蓝鲸智云 版权所有
"""


class User(object):

    username = ''

    def __init__(self, username):
        self.username = username

    def is_authenticated():
        return True


class AnonymousUser(object):

    username = ''

    def is_authenticated():
        return False
