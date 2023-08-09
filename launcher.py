"""Launcher for all program."""

import main
import logger
import time


PERIOD = 600 # in seconds
logger.init()


def run() -> None:
    logger.log.write('LAUNCHER - STARTING.')
    while True:
        logger.log.write('LAUNCHER - RUNNING SIFTER.')
        try:
            main.main()
        except Exception as e:
            logger.log.error(e)
        time.sleep(PERIOD) # don't bully me for this, better give an advice

if __name__ == '__main__':
    run()