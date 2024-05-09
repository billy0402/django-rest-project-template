import logging
import os
import sys

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.getenv("ADMIN_USERNAME")
password = os.getenv("ADMIN_PASSWORD")

if User.objects.filter(**{User.USERNAME_FIELD: username}).exists():
    logging.warning("Admin user is exists.")
    sys.exit()

if username is None or password is None:
    logging.warning("Can't found [ADMIN_USERNAME] or [ADMIN_PASSWORD].")
    sys.exit()

User.objects.create_superuser(
    **{User.USERNAME_FIELD: username},
    password=password,
)

logging.info("Create admin success.")
