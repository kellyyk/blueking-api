# -*- coding: utf-8 -*-
"""
Copyright © 2012-2018 Tencent BlueKing. All Rights Reserved. 蓝鲸智云 版权所有
"""
from esb.component import BaseComponent
from esb.bkauth.models import User, AnonymousUser


class Component(BaseComponent):

    def get_current_user(self):
        if not self.request.wsgi_request:
            return AnonymousUser()

        username = self.request.wsgi_request.g.get('current_user_username')
        if username:
            return User(username)
        else:
            return AnonymousUser()
