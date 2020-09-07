import datetime

from django.db import connection

CURSOR = connection.cursor()
NL = '\n'
ISO_SEP = ' '
MODIFIED = 'modified'


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
        return [field.name for field in self.model._meta.fields]

    @property
    def fields_without_id(self):
        return [field for field in self.fields if field != 'id']

    def field_values(self, c, fields):
        values = []
        for field in fields:
            value = getattr(c, field)

            if isinstance(value, datetime.datetime):
                if field == MODIFIED:
                    value = self.get_current_datetime()
                else:
                    value = self.format_datetime(value)
            values.append(f"'{value}'")
        return values

    def delete(self, c):
        query = f"""
                    DELETE FROM {self.db_table}
                    WHERE id={c.id};
                """
        CURSOR.execute(query)

    def insert(self, c):
        query = f"""
                    INSERT INTO {self.db_table}
                    ({','.join(self.fields_without_id)})
                    VALUES ({','.join(self.field_values(c, self.fields_without_id))});
                """
        CURSOR.execute(query)

    def all(self):
        query = f"""
                    SELECT {','.join(self.fields)}
                    FROM {self.db_table};
                """
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
        CURSOR.execute(query)


class TagManager(CommonManager):
    @property
    def model(self):
        from .models import Tag
        return Tag

    @property
    def db_table(self):
        return self.model._meta.db_table
