# coding=utf-8
#
#

import logging


class Form(object):
    """
    自定义表单验证 以及 传参校验, 可通过 Column的 validator参数自定义验证器
    Example:
    form = Form(
        Column('start', request.args.get('start'), float,
               validator=is_valid_date),
        Column('username', request.args.get('username'), str),
        Column('end', request.args.get('end'), float,
               default=time.time(), required=False, validator=is_valid_date),  # custom validator
        Column('page_size', request.args.get('pageSize'), int,
               required=False, default=25,
               validator=validate_page_size),
        Column('current_page', request.args.get('currentPage'), int,
               required=False, default=0)
    )

    username = form.username    # access parameter
    params = form.to_json()     # to json
    """
    def __init__(self, *columns):
        self.columns = columns

        for column in self.columns:
            try:
                if column.validate():
                    setattr(self, column.name, column.value)
                    continue
                setattr(self, column.name, column.default)
            except Exception as e:
                raise Exception('param <%s> validate error: %s' % (column.name, e))

    def to_json(self):
        return {column.name: getattr(self, 'value', column.default)
                for column in self.columns}

    @property
    def json(self):
        return self.to_json()


class Column(object):
    """
    column/parameter definition
    """
    def __init__(self, name, value, type_,
                 required=True, default=None,
                 validator=None, converter=None):
        self.name = name
        self.type_ = type_
        self.default = default
        self.required = required
        self.converter = converter

        self.value = self.convert(value, type_)
        self.validators = set()

        if validator is not None and callable(validator):
            self.add_validator(validator)
        self.add_validator(self.value_type_validator)

    def add_validator(self, validator):
        self.validators.add(validator)
        return self

    def remove_validator(self, validator):
        self.validators.remove(validator)
        return self

    def convert(self, value, type_):
        """
        转换器，转换失败返回 None
        :param value:
        :param type_:
        :return:
        """
        try:
            if value is None:
                return value

            if self.converter:
                return self.converter(value)

            return type_(value)
        except Exception as e:
            logging.warning('param <%s> convert error: %s', self.name, e)
            return None

    def value_type_validator(self, val):
        if not isinstance(self.value, self.type_):
            raise Exception('except %s, got %s' % (self.type_, type(self.value)))
        return True

    def validate(self):
        if self.required and not self.value:
            raise Exception('param <%s> is required' % self.name)

        if not self.required and not self.value:
            return False

        for validator in self.validators:
            if not validator(self.value):
                raise Exception('validator: %s, value:%s' % (validator.__name__, self.value))

        return True
