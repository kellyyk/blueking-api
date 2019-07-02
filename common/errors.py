# -*- coding: utf-8 -*-
"""
Copyright © 2012-2018 Tencent BlueKing. All Rights Reserved. 蓝鲸智云 版权所有
"""
import copy


class BaseException(Exception):
    pass


class APIError(BaseException):

    def __init__(self, code):
        self.code = code
        BaseException.__init__(self, code.prompt)

    def __str__(self):
        return "<APIError %s[%s]: %s>" % (self.code.status, self.code.code, self.code.prompt)

    def format_prompt(self, prompt=None, replace=False, args=(), kwargs={}):
        self.code = copy.copy(self.code)
        if prompt:
            if replace:
                self.code.prompt = prompt
            else:
                self.code.prompt += ', %s' % prompt

        if args:
            self.code.prompt = self.code.prompt % args
        if kwargs:
            self.code.prompt = self.code.prompt % kwargs
        return self


class ErrorCode(object):

    def __init__(self, code_name, code, prompt, status=200):
        self.code_name = code_name
        self.code = code
        self.prompt = prompt
        self.status = status

    def as_dict(self):
        return {
            'result': False,
            'code': self.code,
            'data': None,
            'message': self.prompt
        }


class ErrorCodes(object):

    error_codes = (
        ErrorCode('COMPONENT_NOT_FOUND', 1306404, 'Not found, component class not found'),
        ErrorCode('ARGUMENT_ERROR', 1306406, 'Parameters error'),

        ErrorCode('COMMON_ERROR', 1306000, 'System error'),

        ErrorCode('EXTERNAL_ERROR', 1306201, 'Request third-party interface error'),
        ErrorCode('TEST_HOST_NOT_FOUND', 1306206, 'Error, the component does not support access third-party test environment'),  # noqa
        ErrorCode('THIRD_PARTY_RESULT_ERROR', 1306208, '%s system interface results in an unknown format'),
    )

    # Init dict
    _error_codes_dict = {}
    for error_code in error_codes:
        _error_codes_dict[error_code.code_name] = error_code

    def __getattr__(self, code_name):
        error_code = self._error_codes_dict[code_name]
        return APIError(error_code)


error_codes = ErrorCodes()


class CommonAPIError(APIError):

    def __init__(self, message, error_code=None, status=None):
        self.message = message
        code = error_codes.COMMON_ERROR.format_prompt(message, replace=True).code
        if error_code:
            code.code = error_code
        if status:
            code.status = status

        super(CommonAPIError, self).__init__(code)
