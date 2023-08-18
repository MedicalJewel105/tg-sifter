"""Launcher for all program."""

import main
import logger
import schedule
import os


os.chdir(os.path.dirname(os.path.realpath(__file__))) # change working direction to folder with this project
PERIOD = 20 # pause interval (in minutes)
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