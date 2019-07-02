# -*- coding: utf-8 -*-
import json

from django.test import TestCase

from .toolkit import configs


class TestCMDB(TestCase):

    def setUp(self):
        self.http_client = configs.http_client

    def test_get_biz_by_id(self):
        params = {
            'bk_username': 'admin',
            'bk_biz_id': 1,
        }
        result = self.http_client.get(path='/c/compapi/cmdb/get_biz_by_id/', params=params)
        print json.dumps(result)
