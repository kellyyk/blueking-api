# -*- coding: utf-8 -*-
"""
Copyright © 2012-2018 Tencent BlueKing. All Rights Reserved. 蓝鲸智云 版权所有
"""
import os

from django.conf import settings


__all__ = ['is_py_file', 'fpath_to_module', 'SmartHost']


def is_py_file(fname):
    return fname.endswith('.py')


def fpath_to_module(fpath):
    prefix = settings.BASE_DIR
    fpath = os.path.normpath(fpath)
    if fpath.startswith(prefix):
        fpath = fpath[len(prefix):]
    fpath = fpath.lstrip(os.path.sep)
    return fpath.replace(os.path.sep, '.').rsplit('.', 1)[0]


class SmartHost(object):

    def __init__(self, host_prod, host_test=None):
        self.hosts_prod = self.make_host_list(host_prod)
        self.hosts_test = self.make_host_list(host_test)
        self._has_test_host = True if self.hosts_test else False

    @staticmethod
    def make_host_list(host):
        if not host:
            return []
        elif isinstance(host, (list, tuple)):
            return host
        else:
            return host.split(';')

    def get_value(self, use_test_env):
        hosts = self.hosts_test if use_test_env else self.hosts_prod
        return hosts[0]

    def has_test_host(self):
        return self._has_test_host
