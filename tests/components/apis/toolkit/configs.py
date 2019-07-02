# -*- coding: utf-8 -*-
from tests.utils.http_client import HttpClient


bk_app_code = 'esb_test'
bk_app_secret = 'xxx'

host = 'http://127.0.0.1:8000/'


http_client = HttpClient(
    host=host,
    bk_app_code=bk_app_code,
    bk_app_secret=bk_app_secret,
)
