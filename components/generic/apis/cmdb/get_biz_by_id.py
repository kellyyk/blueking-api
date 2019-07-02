# -*- coding: utf-8 -*-
from django import forms

from common.forms import BaseComponentForm
from common.constants import API_TYPE_Q
from components.component import Component
from .toolkit import configs


class GetBizById(Component):
    """
    apiLabel 根据业务ID查询业务
    apiMethod GET

    ### 功能描述

    根据业务ID查询业务

    ### 请求参数

    {{ common_args_desc }}

    #### 接口参数

    | 字段     |  类型      | 必选   |  描述      |
    |-----------|------------|--------|------------|
    | bk_biz_id |  int     | 是     | 业务ID |

    ### 请求参数示例

    ```python
    {
        "bk_app_code": "esb_test",
        "bk_app_secret": "xxx",
        "bk_token": "xxx",
        "bk_biz_id": 1
    }
    ```

    ### 返回结果示例

    ```python

    {
        "result": true,
        "code": 0,
        "message": "",
        "data": {
            "bk_biz_id": 1,
            "bk_biz_name": "test",
            "bk_supplier_account": "0"
        }
    }
    ```

    """
    sys_name = configs.SYSTEM_NAME
    api_type = API_TYPE_Q

    class Form(BaseComponentForm):
        bk_biz_id = forms.IntegerField(label='business id', required=True)

        def clean(self):
            data = self.cleaned_data
            return {
                'bk_biz_id': data['bk_biz_id'],
                'bk_supplier_account': '0',
            }

    def handle(self):
        # headers = {
        #     'HTTP_BLUEKING_SUPPLIER_ID': '0',
        #     'BK_USER': self.current_user.username,
        # }
        # self.response.payload = self.outgoing.http_client.get(
        #     host=configs.host,
        #     path='/api/get_biz_by_id/',
        #     params=self.form_data,
        #     headers=headers,
        # )
        self.response.payload = {
            'result': True,
            'data': self.form_data
        }
