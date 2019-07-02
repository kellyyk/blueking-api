# -*- coding: utf-8 -*-
"""
Copyright © 2012-2018 Tencent BlueKing. All Rights Reserved. 蓝鲸智云 版权所有
"""
import json

from django.http import HttpResponse


class JsonResponse(HttpResponse):
    def __init__(self, content, *args, **kwargs):
        content = json.dumps(content, ensure_ascii=False)
        super(JsonResponse, self).__init__(
            content, content_type='application/json; charset=utf-8', *args, **kwargs)
