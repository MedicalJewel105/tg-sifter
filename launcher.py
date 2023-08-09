"""Launcher for all program."""

import main
import logger
import schedule


PERIOD = 20 # pause interval
logger.init()


def launch() -> None:
    logger.log.write('LAUNCHER - STARTING.')
    while True:
        logger.log.write('LAUNCHER - RUNNING SIFTER.')
        schedule.every(PERIOD).minutes.do(run)

def run() -> None:
    try:
        main.main()
    except Exception as e:
        logger.log.error(e)

if __name__ == '__main__':
    launch()