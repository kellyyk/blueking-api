# -*- coding: utf-8 -*-
import copy
import json
import urllib
import urlparse

import requests

from common.log import logger


class HttpClient(object):

    def __init__(self, host=None, bk_app_code='', bk_app_secret=''):
        self.host = host
        self.bk_app_code = bk_app_code
        self.bk_app_secret = bk_app_secret
        self.use_test_env = False

    def set_use_test_env(self, use_test_env):
        self.use_test_env = use_test_env

    def request(self, method, path, params=None, data=None, **kwargs):
        common_args = dict(
            bk_app_code=self.bk_app_code,
            bk_app_secret=self.bk_app_secret,
        )

        headers = kwargs.pop('headers', {})
        if self.use_test_env:
            headers = copy.copy(headers)
            headers['x-use-test-env'] = '1'

        if method == 'GET':
            params = copy.copy(params) or {}
            params.update(common_args)
            data = None
        elif method == 'POST':
            params = copy.copy(params) or {}
            data = copy.copy(data) or {}
            data.update(common_args)
            data = json.dumps(data)

        url = urlparse.urljoin(self.host, path)
        response = requests.request(method, url, params=params, data=data, verify=False, headers=headers, **kwargs)

        logger.info('request method=%s, url=%s\nheaders: %s\nparams: %s\ndata: %s\nresponse: %s\n',
                    method, url, json.dumps(headers), urllib.urlencode(params), data, response.text)

        return response.json()

    def get(self, *args, **kwargs):
        return self.request('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request('POST', *args, **kwargs)
