import os
import arrow
import traceback

LOG_FOLDER = 'log'


class logger:
    """Tool to work with logs. File names: 'DD_MM_YY'."""
    def __init__(self):
        if not os.path.exists(LOG_FOLDER):
            os.mkdir(LOG_FOLDER)

    def _time(self) -> str:
        """Get current time."""
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
        text = 'ERROR!'
        exc_text = ''.join(traceback.format_exception(e))
        self.write(text, exc_text, sep='\n')

    def warning(self, *words, sep = ' ', end = '\n') -> None:
        """Write text to log with a warning.
        Use when handling specified errors."""
        words = ('WARNING!',) + words
        self.write(*words, sep=sep, end=end)

def _test():
    """Test function for this module."""
    l = logger()
    print(l._time())
    print(l._date())
    l.write('abc1')
    l.write('abc2')
    try:
        1 / 0
    except Exception as e:
        l.error(e)
    l.warning('this is a warning')

if __name__ == '__main__':
    _test()