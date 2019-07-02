# -*- coding: utf-8 -*-


def format_resp_dict(resp_data):
    resp_data.setdefault('result', False)
    resp_data.setdefault('data', None)
    resp_data.setdefault('message', '')
    resp_data.setdefault('code', 0 if resp_data['result'] else 1306000)
    return resp_data
