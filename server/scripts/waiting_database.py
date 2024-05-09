import logging
import os
import sys
from time import sleep

from django.db import connections
from django.db.utils import OperationalError

DEFAULT_RETRY_TIME = 30
DEFAULT_SLEEP_TIME = 1

sleep_time = float(os.getenv("WAIT_DB_SLEEP_TIME", DEFAULT_SLEEP_TIME))
retry_time = int(os.getenv("WAIT_DB_RETRY_TIME", DEFAULT_RETRY_TIME))

for connection in connections.all():
    count = 1
    while True:
        logging.info(f"Trying to connect to {connection.alias}, try count {count}.")

        try:
            connection.ensure_connection()
        except OperationalError:
            logging.error(f"Connect to db {connection.alias} fail.")
            if count >= retry_time:
                logging.error("Up to retry limit.")
                sys.exit(1)

            sleep(sleep_time)
            count += 1
        else:
            logging.info(f"Connect to db {connection.alias} success.")
            break
