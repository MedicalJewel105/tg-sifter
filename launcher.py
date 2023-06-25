import sifter
import logger
import time


PERIOD = 600 # seconds


def run() -> None:
    log = logger.logger()
    log.write('[RUNNING PROGRAM]')
    while True:
        try:
            sifter.main()
        except Exception as e:
            log.error(e)
        time.sleep(PERIOD)

if __name__ == '__main__':
    run()