import datetime

from django.db import connection
from django.db.models.fields.related import ForeignKey

CURSOR = connection.cursor()
NL = '\n'
ISO_SEP = ' '
MODIFIED = 'modified'
CREATED = 'created'


class CommonManager:
    @property
    def model(self):
        return CommonManager

    def format_datetime(self, value):
        return value.isoformat(ISO_SEP)

    def get_current_datetime(self):
        return datetime.datetime.today().isoformat(ISO_SEP)

    @property
    def fields(self):
        fields = []
        for field in self.model._meta.fields:
            value = field.name
            if isinstance(field, ForeignKey):
                value = f'{value}_id'
            fields.append(value)
        return fields

    @property
    def fields_without_id(self):
        return [field for field in self.fields if field != 'id']

    @property
    def db_table(self):
        return self.model._meta.db_table

    def field_values(self, c, fields):
        values = []
        for field in fields:
            value = getattr(c, field)
            if isinstance(value, datetime.datetime):
                if field == MODIFIED:
                    value = self.get_current_datetime()
                elif field == CREATED:
                    value = self.format_datetime(value)
                setattr(c, field, value)
            elif value is None and field in [MODIFIED, CREATED]:
                if field == MODIFIED:
                    value = self.get_current_datetime()
                elif field == CREATED:
                    value = self.get_current_datetime()
                setattr(c, field, value)
            values.append(f"'{value}'")
        return values

    def delete(self, c):
        query = f"""
                    DELETE FROM {self.db_table}
                    WHERE id={c.id};
                """
        print(f'delete query: {query}')
        CURSOR.execute(query)

    def all(self):
        query = f"""
                    SELECT {','.join(self.fields)}
                    FROM {self.db_table};
                """
        print(f'all query: {query}')
        CURSOR.execute(query)
        objects = []
        for row in CURSOR.fetchall():
            c = self.model()
            for key, value in zip(self.fields, row):
                setattr(c, key, value)
            objects.append(c)
        return objects

    def get(self, *, id):
        query = f"""
                    SELECT {','.join(self.fields)}
                    FROM {self.db_table}
                    WHERE id={id};
                """
        print(f'get query: {query}')
        CURSOR.execute(query)
        objects = []
        for row in CURSOR.fetchall():
            c = self.model()
            for key, value in zip(self.fields, row):
                setattr(c, key, value)
            objects.append(c)
        return None if not objects else objects[0]

    def update(self, c):
        set_values = f',{NL}'.join([f'{key}={value}' for key, value in zip(
            self.fields_without_id, self.field_values(c, self.fields_without_id)
        )])
        query = f"""
                    UPDATE {self.db_table}
                    SET {set_values}
                    WHERE id={c.id};
                """
        print(f'update query: {query}')
        CURSOR.execute(query)

    def insert(self, c):
        query = f"""
                    INSERT INTO {self.db_table}
                    ({','.join(self.fields_without_id)})
                    VALUES ({','.join(self.field_values(c, self.fields_without_id))});
                """
        print(f'insert query: {query}')
        CURSOR.execute(query)

    def save(self, c):
        print(self)
        print(c)

    def filter(self, *args, **kwargs):
        where_conditions = [f"{key}='{value}'" for key, value in kwargs.items()]
        query = f"""
                    SELECT {','.join(self.fields)}
                    FROM {self.db_table}
                    WHERE {' AND '.join(where_conditions)}
                """
        print(f'filter query: {query}')
        CURSOR.execute(query)
        objects = []
        for row in CURSOR.fetchall():
            c = self.model()
            for key, value in zip(self.fields, row):
                setattr(c, key, value)
            objects.append(c)
        return objects


class TagManager(CommonManager):
    @property
    def model(self):
        from .models import Tag
        return Tag


class UsersConnectManager(CommonManager):
    @property
    def model(self):
        from .models import UsersConnect
        return UsersConnect
