import random
import shutil

import requests
import time

from django.core.management import BaseCommand
from django.db import IntegrityError
from faker import Faker
from transliterate import translit

from dating_site.settings import MEDIA_PREFIX

from matcha.models import User, UserPhoto, UserTag, Tag, UsersConnect, UsersFake, UsersBlackList, Notification

NUM_OF_USERS = 500
# Faker.seed(0)
fake = Faker('ru_RU')


class Command(BaseCommand):
    help = 'Наполняет базу фейковыми данными'

    @staticmethod
    def get_random_bool():
        return bool(random.getrandbits(1))

    @staticmethod
    def update_users():
        user_ids = [user.id for user in User.objects_.all()]
        prev_raw_text = None
        for _ in range(NUM_OF_USERS):
            gender = random.choice([elem[0] for elem in User.GENDERS])
            if gender == User.MAN:
                first_name = fake.first_name_male()
                last_name = fake.last_name_male()
            else:
                first_name = fake.first_name_female()
                last_name = fake.last_name_female()
            username = translit(f'{last_name}{first_name}', 'ru', reversed=True).replace("'", '').lower()
            if User.objects_.filter(username=username):
                continue
            email = f"{username}@{fake.email().split('@')[1]}"
            lat, lon = list(map(float, fake.location_on_land(coords_only=True)))
            city = fake.city_name()
            user = User(
                email=email,
                gender=gender,
                orientation=random.choice([elem[0] for elem in User.ORIENTATIONS]),
                date_of_birth=fake.date_of_birth(),
                info=fake.paragraph(),
                location=city,
                profile_activated=True,
                latitude=lat,
                longitude=lon,
                country='Россия',
                city=city,
                username=username,
                first_name=first_name,
                last_name=last_name,
                is_staff=False,
                is_active=True,
                date_joined=fake.date_time_this_year(),
                password=fake.password(),
                last_login=fake.date_time_this_decade(),
                is_superuser=False
            )
            user.save()
            user_ids.append(user.id)

            user_id = user.id
            file_name = f'{MEDIA_PREFIX}/person_{user_id}.jfif'
            while True:
                time.sleep(1)
                r = requests.get('https://thispersondoesnotexist.com/image', stream=True)
                r.raw.decode_content = True
                if r.status_code != 200 or r.raw == prev_raw_text:
                    continue
                prev_raw_text = r.raw
                with open(file_name, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                break

            UserPhoto(
                title=fake.word(),
                image=f'person_{user_id}.jfif',
                main=True,
                user_id=user_id
            ).save()

            for _ in range(random.randint(1, 4)):
                tag_name = fake.word()
                if not Tag.objects_.filter(name=tag_name):
                    Tag(name=tag_name).save()
                tag = Tag.objects_.filter(name=tag_name)[0]
                try:
                    UserTag(
                        user_id=user_id,
                        tag_id=tag.id
                    ).save()
                except IntegrityError:
                    pass

            if len(user_ids) // 4 >= 1:
                for _ in range(random.randint(1, len(user_ids) // 4)):
                    try:
                        UsersConnect(
                            user_1_id=user_id,
                            user_2_id=user_ids[random.randint(0, len(user_ids) - 1)],
                            type=random.choice([elem[0] for elem in UsersConnect.TYPES])
                        ).save()
                    except IntegrityError:
                        pass

            if user_ids and len(user_ids) % 100 == 0:
                for _ in range(random.randint(1, 3)):
                    try:
                        UsersFake(
                            user_1_id=user_id,
                            user_2_id=user_ids[random.randint(0, len(user_ids) - 1)]
                        ).save()
                    except IntegrityError:
                        pass

            if len(user_ids) // 4 >= 1:
                for _ in range(random.randint(1, len(user_ids) // 4)):
                    try:
                        Notification(
                            user_1_id=user_id,
                            user_2_id=user_ids[random.randint(0, len(user_ids) - 1)],
                            type=random.choice([elem[0] for elem in Notification.TYPES]),
                            was_read=bool(random.getrandbits(1))
                        ).save()
                    except IntegrityError:
                        pass

            if user_ids and len(user_ids) % 50 == 0:
                for _ in range(random.randint(1, len(user_ids) // 8)):
                    try:
                        UsersBlackList(
                            user_1_id=user_id,
                            user_2_id=user_ids[random.randint(0, len(user_ids) - 1)]
                        ).save()
                    except IntegrityError:
                        pass

    def handle(self, *args, **options):
        self.update_users()
