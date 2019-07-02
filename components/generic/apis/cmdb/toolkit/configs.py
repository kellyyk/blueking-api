# -*- coding: utf-8 -*-
from esb.utils import SmartHost


SYSTEM_NAME = 'CMDB'

host = SmartHost(
    host_prod='api.cmdb.domain.com',
    host_test='',
)
