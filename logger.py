import os
import arrow
import traceback
import winsound


LOG_FOLDER = 'log'
MS_ENABLED = False # define whether milliseconds enabled or not 
BEEP_ENABLED = True # beep sound for windows

def init():
    """Initialize log system for use in other modules."""
    global log
    log = logger()

class logger:
    """Tool to work with logs. File names: 'DD_MM_YY'."""
    def __init__(self):
        if not os.path.exists(LOG_FOLDER):
            os.mkdir(LOG_FOLDER)

    def _time(self) -> str:
        """Get current time."""
        if MS_ENABLED:
            now = arrow.utcnow()
            now_time = now.format('HH:mm:ss')
            millis = round(arrow.utcnow().float_timestamp, 3)
            millis -= int(millis)
            return now_time + str(millis)[1:4]
        return arrow.now().format('HH:mm:ss')
    
    def _date(self) -> str:
        """Get current date."""
        return arrow.now().format('DD_MM_YY')
    
    def _join_words(self, words: tuple, sep: str) -> str:
        """Make a string from words."""
        text = ''
        for i in words:
            text += str(i)+sep
        if sep:
            text = text[:-len(sep)]
        return text


    def write(self, *words, sep = ' ', end = '\n') -> None:
        """Write text to log."""
        LOG_FILENAME = self._date() + '.log'
        LOG_PATH = os.path.join(LOG_FOLDER, LOG_FILENAME)

        text = self._join_words(words, sep)

        if not os.path.exists(LOG_PATH):
            mode = 'w'
        else:
            mode = 'a'
        with open(LOG_PATH, mode, encoding='UTF-8') as log:
            log.write(f'[{self._time()}] {text}{end}')
    
    def error(self, e: Exception) -> None:
        """Write error to log.
        Use when handling not specified errors."""
        if BEEP_ENABLED: self.beep(True)
        text = 'ERROR!'
        exc_text = ''.join(traceback.format_exception(e))
        self.write(text, exc_text, sep='\n')

    def warning(self, *words, sep = ' ', end = '\n') -> None:
        """Write text to log with a warning.
        Use when handling specified errors."""
        if BEEP_ENABLED: self.beep(False)
        words = ('WARNING!',) + words
        self.write(*words, sep=sep, end=end)

    def beep(self, is_error: bool) -> None:
        """Beep Boop!"""
        if is_error:
            for _ in range(4):
                winsound.Beep( 1010, 400 )
        else:
            for _ in range(2):
                winsound.Beep( 1010, 250 )

def _test():
    """Developer function."""
    import time
    l = logger()
    print(l._time())
    print(l._date())
    l.write('abc1')
    l.write('abc2')
    try:
        1 / 0
    except Exception as e:
        l.error(e)
    time.sleep(1)
    l.warning('this is a warning')

if __name__ == '__main__':
    _test()