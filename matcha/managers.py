import datetime

from django.db import connection
from django.db.models.fields.related import ForeignKey

from dating_site.settings import verbose_flag

NL = '\n'
ISO_SEP = ' '
MODIFIED = 'modified'
CREATED = 'created'
DATE_JOINED = 'date_joined'


class CommonManager:
    @property
    def model(self):
        return CommonManager

    def format_datetime(self, value):
        return value.isoformat(ISO_SEP)

    def get_current_datetime(self):
        return datetime.datetime.utcnow().isoformat(ISO_SEP)

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
            # print(field, value, type(value))
            if isinstance(value, datetime.datetime):
                value = value.replace(tzinfo=None)
                if field == MODIFIED:
                    value = self.get_current_datetime()
                elif field in [CREATED, DATE_JOINED]:
                    value = self.format_datetime(value)
                setattr(c, field, value)
                values.append(f"'{value}'")
            elif isinstance(value, bool):
                values.append(f'{value}')
            elif value is None and field in [MODIFIED, CREATED, DATE_JOINED]:
                if field in [MODIFIED, CREATED, DATE_JOINED]:
                    value = self.get_current_datetime()
                setattr(c, field, value)
                values.append(f"'{value}'")
            elif value is None:
                values.append("NULL")
            else:
                values.append(f"'{value}'")
        return values

    def delete(self, c):
        query = f"""
                    DELETE FROM {self.db_table}
                    WHERE id={c.id};
                """
        if verbose_flag:
            print(f'delete query: {query}')
        with connection.cursor() as cursor:
            cursor.execute(query)

    def all(self):
        query = f"""
                    SELECT {','.join(self.fields)}
                    FROM {self.db_table};
                """
        if verbose_flag:
            print(f'all query: {query}')
        with connection.cursor() as cursor:
            cursor.execute(query)
            objects = []
            for row in cursor.fetchall():
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
        if verbose_flag:
            print(f'get query: {query}')
        with connection.cursor() as cursor:
            cursor.execute(query)
            objects = []
            for row in cursor.fetchall():
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
        if verbose_flag:
            print(f'update query: {query}')
        with connection.cursor() as cursor:
            cursor.execute(query)

    def insert(self, c):
        query = f"""
                    INSERT INTO {self.db_table}
                    ({','.join(self.fields_without_id)})
                    VALUES ({','.join(self.field_values(c, self.fields_without_id))});
                """
        if verbose_flag:
            print(f'insert query: {query}')
        with connection.cursor() as cursor:
            cursor.execute(query)
            setattr(c, 'id', cursor.lastrowid)
        c.save()

    def filter(self, *args, **kwargs):
        if not kwargs:
            return
        where_conditions = []
        for key, value in kwargs.items():
            key, *op = key.rsplit('__', maxsplit=1)
            if op:
                op = op[0]
                if op == 'gte':
                    where_condition = f"{key}>='{value}'"
                elif op == 'gt':
                    where_condition = f"{key}>'{value}'"
                elif op == 'lte':
                    where_condition = f"{key}<='{value}'"
                elif op == 'lt':
                    where_condition = f"{key}<'{value}'"
                elif op == 'in':
                    objs = ', '.join([f"'{obj}'" for obj in value])
                    where_condition = ''
                    if objs:
                        where_condition = f"{key} IN ({objs})"
                elif op == 'icontains':
                    where_condition = f"LOWER({key}) LIKE '%{value}%'"
                else:
                    raise ValueError(f"Unknown op {op}")
            else:
                where_condition = f"{key}='{value}'"
            if where_condition:
                where_conditions.append(where_condition)
        with connection.cursor() as cursor:
            objects = []
            if where_conditions:
                query = f"""
                    SELECT {','.join(self.fields)}
                    FROM {self.db_table}
                    WHERE {' AND '.join(where_conditions)}
                """
                if verbose_flag:
                    print(f'filter query: {query}')
                cursor.execute(query)
                for row in cursor.fetchall():
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


class UserTagManager(CommonManager):
    @property
    def model(self):
        from .models import UserTag
        return UserTag


class UsersConnectManager(CommonManager):
    @property
    def model(self):
        from .models import UsersConnect
        return UsersConnect


class UsersFakeManager(CommonManager):
    @property
    def model(self):
        from .models import UsersFake
        return UsersFake


class UsersBlackListManager(CommonManager):
    @property
    def model(self):
        from .models import UsersBlackList
        return UsersBlackList


class UserPhotoManager(CommonManager):
    @property
    def model(self):
        from .models import UserPhoto
        return UserPhoto


class UserManager(CommonManager):
    @property
    def model(self):
        from .models import User
        return User


class NotificationManager(CommonManager):
    @property
    def model(self):
        from .models import Notification
        return Notification


class MessageManager(CommonManager):
    @property
    def model(self):
        from .models import Message
        return Message
