import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eleventh_project.settings')

import django
django.setup()

from basic_app.models import User
from faker import Faker
fakegen = Faker()

if __name__ == '__main__':
    print("Populator in progress...")
    print("Populator done!")
