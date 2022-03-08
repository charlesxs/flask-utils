# coding=utf-8
#
#

from flask_sqlalchemy.model import Model


class Serializer:
    """
    Serializer类实现 由model 到json以及由json到model的转换

    Example:
    class MyModelSerializer(Serializer):
        class Meta:
            model_class = MyModel
            exclude_columns = ['id']

    model = MyModel.query.first()
    serial = MyModelSerializer(model)
    json_data = serial.to_json()


    form_data = request.get_json()
    serial = MyModelSerializer(data=form_data)
    model = serial.to_model()
    """
    def __init__(self, model=None, data=None, model_class=None):
        self.model = model
        self.data = data

        self.model_class = getattr(self.Meta, 'model_class', None) or model_class
        if self.model_class is None or not issubclass(self.model_class, Model):
            raise TypeError("expect db.Model's instance")

        self._table = self.model_class.__table__
        self.exclude_columns = getattr(self.Meta, 'exclude_columns', tuple())

    @property
    def columns(self):
        return list(self._table.columns.keys())

    def to_json(self):
        if self.model is None:
            raise ValueError('expect model is not None')
        return {column: getattr(self.model, column)
                for column in self.columns if column not in self.exclude_columns}

    def to_model(self):
        if self.data is None:
            raise ValueError('expect data is not None')
        model = self.model_class()
        for column in self.columns:
            if column in self.exclude_columns or column not in self.data:
                continue
            setattr(model, column, self.data[column])
        return model

    class Meta:
        pass

