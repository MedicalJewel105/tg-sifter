from os import path, mkdir
import logger


log = logger.logger()
DATA_FOLDER = 'data'
CHANNELS_FILE = 'channels.csv'
CHANNELS_PATH = path.join(DATA_FOLDER, CHANNELS_FILE)
CSV_SEP = ';'


class database:
    def __init__(self):
        self.channels_data, self.__broken_channels = self.__load()

    def __load(self) -> tuple:
        """Load .csv database with channels & last post ids."""
        log.write('DB - LOADING...')
        if not path.exists(CHANNELS_PATH):
            log.write(f'ERROR! {CHANNELS_PATH} FILE NOT FOUND.')
            exit()
        with open(CHANNELS_PATH, 'r') as f:
            lines = list(map(lambda x: x.strip('\n'), f.readlines()))
        if not lines:
            log.write('ERROR! DB FILE IS EMPTY.')
            exit()
        
        res = []
        broken = []
        i = 0
        for line in lines:
            x = line.split(';') # [channel_shortcut, last_parsed_message]
            if len(x) == 2 and x[1].isnumeric():
                res.append([x[0], int(x[1])])
            else:
                log.write(f'WARNING! UNABLE TO PARSE "{line}" ({i}) FROM DB.')
                broken.append(line)
            i += 1
        log.write('DB - LOADED.')
        return res, broken
    

    def save(self) -> None:
        """Save .csv database with channels & last post ids."""
        log.write('DB - SAVING...')
        if not path.isdir(DATA_FOLDER):
            log.write(f'WARNING! {DATA_FOLDER} FOLDER DOES NOT EXIST.')
            mkdir(DATA_FOLDER)
        with open(CHANNELS_PATH, 'w') as f:
            for i in self.channels_data:
                line = str(i[0]) + CSV_SEP + str(i[1]) + '\n'
                f.write(line)
            for i in self.__broken_channels:
                f.write(i)
        log.write('DB - SAVED.')