import random

from django.core.management import BaseCommand
from faker import Faker

from matcha.models import User, UserPhoto

NUM_OF_USERS = 500
fake = Faker('ru_RU')


class Command(BaseCommand):
    help = 'Наполняет базу фейковыми данными'

    @staticmethod
    def get_random_bool():
        return bool(random.getrandbits(1))

    def update_users(self):
        for _ in range(NUM_OF_USERS):
            user = User(
                email=fake.email(),
                gender=random.choice([elem[0] for elem in User.GENDERS]),
                orientation=random.choice([elem[0] for elem in User.ORIENTATIONS]),
                date_of_birth=fake.date_of_birth(),
                info=fake.paragraph(),
                location=fake.address(),
                profile_activated=self.get_random_bool(),
                latitude=float(fake.latitude()),
                longitude=float(fake.longitude()),
                country=fake.country(),
                city=fake.city(),
                username=fake.user_name(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_staff=self.get_random_bool(),
                is_active=self.get_random_bool(),
                date_joined=fake.date_time_this_year(),
                password=fake.password(),
                last_login=fake.date_time_this_decade(),
                is_superuser=False
            )
            user.save()
            # UserPhoto(
            #     title=fake.word(),
            #     image='/media/images/',
            #     main=True,
            #     user_id=user.id
            # ).save()


    def handle(self, *args, **options):
        self.update_users()
