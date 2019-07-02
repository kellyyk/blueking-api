# -*- coding: utf-8 -*-
"""
Copyright © 2012-2018 Tencent BlueKing. All Rights Reserved. 蓝鲸智云 版权所有
"""
import json
from urlparse import urljoin

import requests
from django.utils.encoding import smart_str

from common.errors import error_codes
from common.log import logger, logger_api


class HttpClient(object):

    def __init__(self, component):
        self.component = component

    def get(self, *args, **kwargs):
        return self.request('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request('POST', *args, **kwargs)

    def request(self, method, host, path, params=None, data=None, headers={},
                response_type='json', response_encoding=None, request_encoding=None,
                cert=None, timeout=None, allow_non_200=False):
        system_name = self.component.sys_name
        component_name = self.component.get_component_name()
        url = self.make_url(host, path, use_test_env=self.component.request.use_test_env)
        if request_encoding:
            if isinstance(params, dict):
                params = self.encode_dict(params, encoding=request_encoding)
            if isinstance(data, dict):
                data = self.encode_dict(data, encoding=request_encoding)

        try:
            resp = requests.request(
                method, url,
                params=params,
                data=data,
                headers=headers,
                cert=cert,
                timeout=timeout,
                verify=False,
            )

            if response_encoding:
                resp.encoding = response_encoding

            resp_text = resp.text
            resp_status_code = resp.status_code

            if not allow_non_200 and resp_status_code != 200:
                raise Exception(u'Status code %s' % resp_status_code)
            result = self.format_resp(resp_text, response_type=response_type)
            request_exception = None
        except Exception as e:
            logger.exception('Error occured when sending request to %s', url)
            request_exception = e
            result = None
            resp = None
            resp_status_code = -1
            resp_text = ''

        req_params = params or data
        if not isinstance(req_params, basestring):
            req_params = json.dumps(req_params)

        api_log = {
            'type': 'pyls-comp-api',
            'request_id': self.component.request.request_id,
            'req_app_code': self.component.request.app_code,
            'req_system_name': system_name,
            'req_component_name': component_name,
            'req_url': url,
            'req_params': req_params,
            'req_status': resp_status_code,
            'req_response': resp_text,
            'req_exception': smart_str(request_exception) if request_exception else None,
        }
        logger_api.info(json.dumps(api_log))

        if request_exception:
            raise error_codes.EXTERNAL_ERROR.format_prompt(
                u'Component request third-party system [%s] interface [%s] error: %s, '
                u'please try again later or contact component developer.'
                % (system_name, component_name, request_exception), replace=True
            )
        return result

    @staticmethod
    def make_url(host, path, use_test_env):
        if use_test_env and not host.has_test_host():
            raise error_codes.TEST_HOST_NOT_FOUND.format_prompt()

        host = host.get_value(use_test_env=use_test_env)
        if not host.startswith('http'):
            host = 'http://%s' % host
        return urljoin(host, path)

    @staticmethod
    def format_resp(resp_text, encoding='utf-8', response_type='json'):
        if response_type == 'json':
            return json.loads(resp_text)
        else:
            return resp_text

    @staticmethod
    def encode_dict(d, encoding='utf-8'):
        result = {}
        for k, v in d.iteritems():
            if isinstance(v, unicode):
                result[k] = v.encode(encoding)
            else:
                result[k] = v
        return result


class RequestHelperClient(object):

    def __init__(self, component):
        self.component = component

    def request(self, handler, action='', args=[], kwargs={}, timeout=None, api_name='', is_response_parse=True):  # noqa
        system_name = self.component.sys_name
        component_name = api_name or self.component.get_component_name()

        request_url = ''
        request_exception = None
        request_params = {'action': action, 'args': args, 'kwargs': kwargs}
        resp_text = ''
        resp_status_code = -1
        result = None
        try:
            if action:
                resp = getattr(handler, action)(*args, **kwargs)
            else:
                resp = handler(*args, **kwargs)
        except Exception as e:
            logger.exception('error occured when request sys_name: %s, component_name: %s', system_name, component_name)
            request_exception = e
        else:
            if is_response_parse:
                request_url = resp.get('request_url', '')
                request_exception = resp.get('request_exception', None)
                request_params = resp.get('request_params') if hasattr(resp, 'request_params') else request_params
                resp_text = resp.get('resp_text', '')
                resp_status_code = resp.get('resp_status_code', -1)
                result = resp.get('result')
            else:
                resp_status_code = 200
                if isinstance(resp, basestring):
                    resp_text = resp
                else:
                    try:
                        resp_text = json.dumps(resp)
                    except:
                        resp_text = str(resp)

                result = resp

        if not isinstance(request_params, basestring):
            try:
                request_params = json.dumps(request_params)
            except:
                request_params = str(request_params)

        api_log = {
            'type': 'pyls-comp-api',
            'request_id': self.component.request.request_id,
            'req_app_code': self.component.request.app_code,
            'req_system_name': system_name,
            'req_component_name': component_name,
            'req_params': request_params,
            'req_status': resp_status_code,
            'req_response': resp_text,
            'req_exception': smart_str(request_exception) if request_exception else None,
            'req_url': request_url,
        }
        logger_api.info(json.dumps(api_log))

        if request_exception:
            raise error_codes.EXTERNAL_ERROR.format_prompt(
                u'Component request third-party system [%s] interface [%s] error: %s, '
                u'please try again later or contact component developer.'
                % (system_name, component_name, request_exception), replace=True
            )
        return result
