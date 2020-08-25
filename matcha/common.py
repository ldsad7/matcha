from easy_thumbnails.files import get_thumbnailer
from django.utils.safestring import mark_safe
from matcha.exceptions import IncorrectArgument, NoSuchId


def get_by_model_and_id(model, _id):
    try:
        _id = int(_id)
    except Exception:
        raise IncorrectArgument()
    try:
        return model.objects.get(id=_id)
    except model.DoesNotExist:
        raise NoSuchId()


def get_thumb(image, width, height, crop=True):
    if image:
        try:
            thumb = get_thumbnailer(image).get_thumbnail({'size': (width, height), 'crop': crop})
            return mark_safe('<img src="%s">' % thumb.url)
        except Exception as e:
            print(e)
            return None
    else:
        return ''
