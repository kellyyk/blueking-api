# -*- coding: utf-8 -*-
"""
Copyright © 2012-2018 Tencent BlueKing. All Rights Reserved. 蓝鲸智云 版权所有
"""
import json
import uuid

from django.views.generic import View

from common.django_utils import JsonResponse
from common.base_utils import str_bool, FancyDict
from common.errors import error_codes, CommonAPIError, APIError
from common.log import logger
from esb.utils.utils import format_resp_dict
from esb.component import get_components_manager, CompRequest


class APIView(View):

    def get(self, request, *args, **kwargs):
        return self._request('GET', request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self._request('POST', request, *args, **kwargs)

    def _request(self, method, request, system_name, component_name):
        components_manager = get_components_manager()
        comp_cls = components_manager.get_comp_by_compname(system_name, component_name)
        if not comp_cls:
            raise error_codes.COMPONENT_NOT_FOUND.format_prompt('system_name: %s, component_name: %s' % (system_name.upper(), component_name))  # noqa
        comp = comp_cls()
        self.patch_request_common(request)
        comp.set_request(CompRequest(wsgi_request=request))
        try:
            response = comp.invoke()
        except APIError as e:
            response = e.code.as_dict()
        except:
            logger.exception('Request exception, request_id=%s, path=%s' % (request.g.request_id, request.path))
            response = CommonAPIError('Component error, please contact the component developer').code.as_dict()

        response['request_id'] = request.g.request_id
        response = format_resp_dict(response)
        return JsonResponse(response)

    def patch_request_common(self, request):
        request.g.request_id = uuid.uuid4().get_hex()
        request.g.kwargs = FancyDict(self.get_request_params(request))
        request.g.current_user_username = request.g.kwargs.get('bk_username') or request.g.kwargs.get('username', '')
        request.g.app_code = request.g.kwargs.get('bk_app_code') or request.g.kwargs.get('app_code')
        request.g.use_test_env = str_bool(request.META.get('HTTP_X_USE_TEST_ENV'))

    def get_request_params(self, request):
        if request.method == 'GET':
            return dict(request.GET.items())

        if request.body and request.body.strip().startswith('{'):
            try:
                return json.loads(request.body)
            except:
                raise error_codes.COMMON_ERROR.format_prompt('Request JSON string is wrong in format, which cannot be analyzed.', replace=True)  # noqa
        else:
            return dict(request.POST.items())
