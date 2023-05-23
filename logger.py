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
    
    def write(self, *words, sep = ' ') -> None:
        """Write text to log."""
        LOG_FILENAME = self._date() + '.log'
        LOG_PATH = os.path.join(LOG_FOLDER, LOG_FILENAME)

        text = ''
        for i in words:
            text += str(i)+sep
        if sep:
            text = text[:-len(sep)]

        if not os.path.exists(LOG_PATH):
            mode = 'w'
        else:
            mode = 'a'
        with open(LOG_PATH, mode) as log:
            log.write(f'[{self._time()}] {text}\n')
    
    def error(self, e: Exception) -> None:
        """Write error to log."""
        text = 'ERROR!'
        exc_text = ''.join(traceback.format_exception(e))
        self.write(text, exc_text, sep='\n')


def _test():
    """Test function."""
    l = logger()
    print(l._time())
    print(l._date())
    l.write('abc1')
    l.write('abc2')

if __name__ == '__main__':
    _test()