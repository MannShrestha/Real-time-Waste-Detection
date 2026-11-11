from wasteDetection.logger import logging

# logging.info("First print")

import sys

from wasteDetection.exception import AppException
from wasteDetection.logger import logging


try:

    num = 10 / 0

except Exception as e:

    logging.error(
        AppException(
            e,
            sys
        )
    )