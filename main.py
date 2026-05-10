# main.py

from sensor.exception import SensorException
import sys
import logging
from sensor.logger import  logging

def test_exception():
    try:
        logging.info("Error aa rahi he")
        a = 1 / 0

    except Exception as e:
        raise SensorException(e, sys)


if __name__ == "__main__":

    try:
        test_exception()

    except Exception as e:
        print(e)