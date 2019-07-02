# -*- coding: utf-8 -*-
"""
Bases for Component Forms

Copyright © 2012-2018 Tencent BlueKing. All Rights Reserved. 蓝鲸智云 版权所有
"""
import re
import json

from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.encoding import force_unicode, smart_unicode
from django.forms import Field
from django.forms.utils import ErrorDict

from common.base_utils import FancyDict, str_bool
from common.errors import CommonAPIError


def get_error_prompt(form):
    content = []
    fields = form.fields.keys()
    for k, v in sorted(form.errors.items(), key=lambda x: fields.index(x[0])
                       if x[0] in fields else -1):
        _msg = force_unicode(v[0])
        b_field = form._safe_get_field(k)
        messages = {}
        if b_field:
            for c in reversed(b_field.field.__class__.__mro__):
                messages.update(getattr(c, 'default_error_messages', {}))

        if b_field and _msg in messages.values():
            content.append(u'%s [%s] %s' % (b_field.label, b_field.name, _msg))
        else:
            content.append(u'%s' % _msg)
    return force_unicode(content[0])


class BaseComponentForm(forms.Form):
    field_collections = ()

    def __init__(self, *args, **kwargs):
        super(BaseComponentForm, self).__init__(*args, **kwargs)
        for collection in self.field_collections:
            for name, field in collection.fields:
                self.fields[name] = field

    get_error_prompt = get_error_prompt

    def _safe_get_field(self, field):
        return self[field] if field in self.fields else None

    @property
    def fancy_cleaned_data(self):
        return FancyDict(self.cleaned_data)

    def clean(self):
        data = super(BaseComponentForm, self).clean()
        for collection in self.field_collections:
            collection.refine_data(data)
        return data

    @classmethod
    def from_request(cls, request):
        if hasattr(request, 'g'):
            return cls(request.g.kwargs)
        return cls(request.kwargs)

    def get_cleaned_data_or_error(self, status=None):
        if self.is_valid():
            return self.cleaned_data
        else:
            raise CommonAPIError(self.get_error_prompt(), status=status)

    def full_clean(self):
        self._errors = ErrorDict()
        if not self.is_bound:
            return
        self.cleaned_data = {}
        if self.empty_permitted and not self.has_changed():
            return
        self._clean_fields()
        if not self.is_valid():
            return

        self._clean_form()
        self._post_clean()
        if self._errors:
            del self.cleaned_data

    def get_cleaned_data_when_exist(self, keys=[]):
        """
        Get cleaned_data of key when key in self.data
        """
        keys = keys or self.fields.keys()
        if isinstance(keys, dict):
            return dict([
                (key_dst, self.cleaned_data[key_src])
                for key_src, key_dst in keys.items()
                if key_src in self.data
            ])
        else:
            return dict([
                (key, self.cleaned_data[key])
                for key in keys
                if key in self.data
            ])


class ListField(Field):
    default_error_messages = {
        'invalid_list': 'Must be a list',
    }
    delimiter = re.compile(r'[^,;\n\r ]+')

    def __init__(self, delimiter='', *args, **kwargs):
        if delimiter:
            self.delimiter = re.compile(delimiter)
        super(ListField, self).__init__(*args, **kwargs)

    def to_python_unicode(self, value):
        if value in validators.EMPTY_VALUES:
            return ''
        return smart_unicode(value)

    def to_python(self, value):
        if isinstance(value, (list, tuple)):
            return list(value)

        try:
            result = json.loads(value)
            if isinstance(result, list):
                return result
        except:
            pass

        value = self.to_python_unicode(value).strip()
        if not value:
            return []
        return self.delimiter.findall(value)


class TypeCheckField(Field):
    invalid_type_msg = 'Must be the specified parameter data type'
    default_error_messages = {
        'invalid_list_type': '%s list' % invalid_type_msg,
        'invalid_dict_type': '%s dict' % invalid_type_msg,
        'invalid_type': invalid_type_msg,
    }

    def __init__(self, promise_type=None, *args, **kwargs):
        self.promise_type = promise_type
        super(TypeCheckField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value in validators.EMPTY_VALUES:
            return self.promise_type()

        if self.promise_type and not isinstance(value, self.promise_type):
            if self.promise_type in [list, dict]:
                raise ValidationError('%s %s' % (self.invalid_type_msg, self.promise_type.__name__))
            else:
                raise ValidationError(self.invalid_type_msg)

        return value


class DefaultBooleanField(Field):
    def __init__(self, default=False, *args, **kwargs):
        self.default = default
        super(DefaultBooleanField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        value = super(DefaultBooleanField, self).to_python(value)
        if value in validators.EMPTY_VALUES:
            return self.default

        value = str_bool(value)
        return value
