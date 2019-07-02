# -*- coding: utf-8 -*-
"""
Copyright © 2012-2018 Tencent BlueKing. All Rights Reserved. 蓝鲸智云 版权所有
"""
from common.django_utils import JsonResponse
from common.base_utils import FancyDict
from common.errors import APIError
from esb.utils.utils import format_resp_dict


class APICommonMiddleware(object):

    def process_request(self, request):
        request.g = FancyDict()

    def process_exception(self, request, exception):
        if isinstance(exception, APIError):
            response = format_resp_dict(exception.code.as_dict())
            return JsonResponse(response, status=exception.code.status)
