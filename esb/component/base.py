# -*- coding: utf-8 -*-
"""
Copyright © 2012-2018 Tencent BlueKing. All Rights Reserved. 蓝鲸智云 版权所有
"""
import os
import copy
from importlib import import_module

from django.conf import settings

from common.errors import APIError
from common.base_utils import smart_lower, FancyDict
from common.log import logger
from esb.outgoing import HttpClient
from esb.utils import is_py_file, fpath_to_module


class BaseComponent(object):

    sys_name = 'UNKNOWN'
    api_type = 'unknown'
    name_prefix = ''
    Form = None

    def __init__(self, request=None, current_user=None):
        self.request = request
        self.response = CompResponse()
        self.form_data = {}
        self.outgoing = FancyDict()
        self.outgoing.http_client = HttpClient(self)

        self._current_user = current_user

    def set_request(self, request):
        assert isinstance(request, CompRequest)
        self.request = request

    def get_current_user(self):
        pass

    @property
    def current_user(self):
        return self._current_user

    @current_user.setter
    def current_user(self, value):
        self._current_user = value

    def invoke(self, kwargs={}, use_test_env=False, request_id=None, app_code=''):
        if not self.request:
            if isinstance(kwargs, dict):
                kwargs = FancyDict(kwargs)

            self.set_request(
                CompRequest(
                    input=kwargs,
                    use_test_env=use_test_env,
                    request_id=request_id,
                    app_code=app_code,
                )
            )
        if not self._current_user:
            self._current_user = self.get_current_user()

        self.validate_input()
        try:
            self.handle()
        except APIError as e:
            self.response.payload = e.code.as_dict()
        return self.response.get_payload()

    def invoke_other(self, *args, **kwargs):
        return self._invoke_other(*args, **kwargs)

    def _invoke_other(self, component_name, kwargs={}, use_test_env=None, timeout=None):
        comp_obj = self.prepare_other(
            component_name,
            kwargs=kwargs,
            use_test_env=use_test_env,
        )
        return comp_obj.invoke()

    def prepare_other(self, component_name, kwargs={}, use_test_env=None, timeout=None):
        components_manager = get_components_manager()
        comp_class = components_manager.get_comp_by_name(component_name)

        if not comp_class:
            raise ValueError('No component can be found via name=%s' % (component_name))

        if use_test_env is None:
            use_test_env = self.request.use_test_env

        if isinstance(kwargs, dict):
            kwargs = FancyDict(kwargs)

        comp_obj = comp_class()
        comp_obj.current_user = self.current_user
        comp_obj.set_request(
            CompRequest(
                input=kwargs,
                use_test_env=use_test_env,
                request_id=self.request.request_id,
                app_code=self.request.app_code,
            )
        )
        return comp_obj

    def validate_input(self):
        if self.Form:
            self.form_data = self.Form.from_request(self.request).get_cleaned_data_or_error()
            self.request.kwargs.update(self.form_data)

    def handle(self):
        pass

    @classmethod
    def get_component_name(cls):
        return smart_lower(cls.__name__)


class CompRequest(object):

    SENSITIVE_PARAMS_KEY = [
        'app_secret',
        'signature',
        'bk_nonce',
        'bk_timestamp',
        'bk_app_secret',
        'bk_signature',
    ]

    def __init__(self, wsgi_request=None, input=None, use_test_env=False, request_id=None, app_code=''):
        self.wsgi_request = wsgi_request
        if self.wsgi_request:
            self.kwargs = copy.copy(self.wsgi_request.g.kwargs)
            self.kwargs = self._clean_params(self.kwargs)
            self.use_test_env = self.wsgi_request.g.use_test_env
            self.request_id = self.wsgi_request.g.request_id
            self.app_code = self.wsgi_request.g.get('app_code', '')
        else:
            self.kwargs = copy.copy(input) or FancyDict()
            self.use_test_env = use_test_env
            self.request_id = request_id
            self.app_code = app_code

    def _clean_params(self, params):
        for key in self.SENSITIVE_PARAMS_KEY:
            params.pop(key, None)
        return params


class CompResponse(object):

    def __init__(self):
        self.payload = {}
        self.headers = {}

    def get_payload(self):
        return self.payload


class ComponentsManager(object):

    def __init__(self, ):
        self.name_component_map = {}

    def __str__(self):
        return '<ComponentsManager>'

    def get_comp_by_name(self, name):
        return self.name_component_map.get(name)

    def get_comp_by_compname(self, system_name, component_name):
        component_codename = self.get_component_codename(
            settings.COMPONENT_CONFIG.get('name_prefix', ''),
            system_name,
            component_name,
        )
        return self.name_component_map.get(component_codename)

    def register_by_config(self):
        component_base_path = settings.COMPONENT_CONFIG['component_base_path']

        for current_folder, folders, files in os.walk(component_base_path):
            for filename in files:
                filename = os.path.join(current_folder, filename)
                if self.should_register(filename):
                    try:
                        module = import_module(fpath_to_module(filename))
                        self.register_by_module(module)
                    except:
                        logger.exception('Error when register file %s, skip', filename)

    def should_register(self, filename):
        fpath, base_fname = os.path.split(filename)
        if fpath.endswith('/toolkit'):
            return False
        return is_py_file(base_fname) and not base_fname.startswith('_')

    def register_by_module(self, module):
        module_name = module.__name__
        package_name = module_name.rsplit('.', 1)[1]
        comp_cls_name = ''.join(package_name.title().split('_'))
        comp_cls = getattr(module, comp_cls_name, None)

        if not comp_cls:
            logger.error('module [%s] does not contain component class [%s], please check', module_name, comp_cls_name)
            return

        if not (hasattr(comp_cls, 'handle') and
                issubclass(comp_cls, BaseComponent) and
                comp_cls.__module__ == module_name):
            logger.error('module [%s] component class [%s], has no handle function, '
                         'or is not subclass of BaseComponent, '
                         'or not defined in this module, please check', module_name, comp_cls_name)
            return

        self.register(comp_cls)

    def register(self, comp_class):
        component_codename = self.get_component_codename(
            settings.COMPONENT_CONFIG.get('name_prefix', ''),
            comp_class.sys_name.lower(),
            comp_class.get_component_name(),
        )
        self.name_component_map[component_codename] = comp_class

    def get_component_codename(self, name_prefix, system_name, component_name):
        return '%s%s.%s' % (name_prefix, system_name, component_name)

    def get_registed_components(self):
        return self.name_component_map


_components_manager = None


def get_components_manager():
    global _components_manager
    if _components_manager is None:
        _components_manager = ComponentsManager()
        _components_manager.register_by_config()
    return _components_manager
