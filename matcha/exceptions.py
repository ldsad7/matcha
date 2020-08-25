from rest_framework.exceptions import APIException


class IncorrectArgument(APIException):
    status_code = 400
    default_detail = 'Incorrect argument'


class NoSuchId(APIException):
    status_code = 400
    default_detail = 'There is no such id in the database.'


class NoSuchParameter(APIException):
    status_code = 400
    default_detail = 'There is no such parameter in the database.'
