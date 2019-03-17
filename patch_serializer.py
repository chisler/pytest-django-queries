import inspect


class ExtraQueryError(object):
    def __init__(self, serializer_name, field, function_name, queries, path):
        self.serializer_name = serializer_name
        self.field = field
        self.function_name = function_name
        self.queries = queries
        self.path = path

    def suggest_to_prefetch(self):
        raise NotImplementedError()

    def to_row(self):
        return [
            self.serializer_name,
            self.field,
            self.function_name,
            str(len(self.queries)),
        ]

    def __str__(self):
        return f"{self.serializer_name} when calling `{self.field}`.{self.function_name} required {len(self.queries)}"


def watch_function_query_count(serializer, function, field_name, plugin):
    from django.db import connection

    connection.force_debug_cursor = True

    def wrap(*args, **kwargs):
        before = len(connection.queries)
        ret = function(*args, **kwargs)
        extra_query_count = len(connection.queries) - before
        if extra_query_count:

            plugin.add_extra_query(
                ExtraQueryError(
                    serializer_name=serializer.__class__.__name__,
                    field=field_name,
                    function_name=function.__name__,
                    queries=connection.queries[before:],
                    path=inspect.getfile(serializer.__class__),
                )
            )

        return ret

    return wrap


def patch_serializer(plugin):
    from rest_framework.serializers import Serializer

    original_to_representation = Serializer.to_representation

    def new_to_representation(self, instance):
        """
        This code relies on Django 2 implementation of Serializer.to_representation
        """

        fields = self._readable_fields

        for field in fields:
            field.get_attribute = watch_function_query_count(
                self, field.get_attribute, field.field_name, plugin
            )
            field.to_representation = watch_function_query_count(
                self, field.to_representation, field.field_name, plugin
            )

        return original_to_representation(self, instance)

    Serializer.to_representation = new_to_representation
