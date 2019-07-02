# -*- coding: utf-8 -*-
import json

from django.test import TestCase

from .toolkit import configs
class TestCMDBV2(TestCase):

    def setUp(self):
        self.http_client = configs.http_client

    def test_get_biz_by_id(self):
        from components.generic.apis.cmdbv2.get_biz_by_id import GetBizById
        params = {
            'bk_username': 'admin',
            'bk_biz_id': 1,
        }
        result = self.http_client.get(path='/c/compapi/cmdbv2/get_biz_by_id/', params=params)
        # result = GetBizById().invoke(kwargs=params)

        print json.dumps(result)
