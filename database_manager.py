"""Module to communicate with database."""

from os import path, mkdir
import logger
import json


log = logger.logger()
DATA_FOLDER = 'data'
CHANNELS_FILE = 'channels.json'
CHANNELS_PATH = path.join(DATA_FOLDER, CHANNELS_FILE)


class channel_data:
    class _spam_options:
        def __init__(self, y: dict):
            self.has_link = y.get('has_link', None)
            self.has_photo = y.get('has_photo', None)
            self.has_video = y.get('has_video', None)
            self.has_poll = y.get('has_poll', None)
            self.has_text = y.get('has_text', None)
            self.allowed_links = y.get('allowed_links', [])
            self.spam_match = y.get('spam_match', 0.8)

    def __init__(self, x: dict):
        self.is_ok = True
        self.name = x.get('name', '')
        self.last_post_id = x.get('last_post_id', 0)
        self.spam_options = self._spam_options(x.get('spam_options', {}))

        self.is_ok = bool(self.name) and bool(x.get('spam_options', {}))
    
    def to_json(self) -> dict:
        """Transform object into .json format."""
        data = {
            'name': self.name,
            'last_post_id': self.last_post_id,
            'spam_options': {
                'has_link': self.spam_options.has_link,
                'has_photo': self.spam_options.has_photo,
                'has_video': self.spam_options.has_video,
                'has_poll': self.spam_options.has_poll,
                'has_text': self.spam_options.has_text,
                'spam_match': self.spam_options.spam_match,
                'allowed_links': self.spam_options.allowed_links
            }
        }
        return data
        
class database:
    def __init__(self):
        self.channels = []
        self.__load()

    def __load(self) -> None:
        """Load .json DB and create channel objects."""
        log.write('DB - LOADING...')
        if not path.exists(CHANNELS_PATH):
            log.write(f'ERROR! {CHANNELS_PATH} FILE NOT FOUND.')
            exit()
        with open(CHANNELS_PATH, 'r') as f:
            data = json.load(f)
        for x in data:
            self.channels.append(channel_data(x))
        log.write('DB - LOADED.')

    def save(self) -> None:
        """Save .json database with channels & last post ids."""
        log.write('DB - SAVING...')
        if not path.isdir(DATA_FOLDER):
            log.write(f'WARNING! {DATA_FOLDER} FOLDER DOES NOT EXIST.')
            mkdir(DATA_FOLDER)
        json_data = [i.to_json() for i in self.channels]
        with open(CHANNELS_PATH, 'w') as f:
            json.dump(json_data, f, indent=4)
        log.write('DB - SAVED.')

def __test():
    """Developer function."""
    k = database()
    print(k.channels[0].to_json())
    k.channels[0].spam_options.allowed_links.append('aaa.com')
    k.save()

if __name__ == '__main__':
    __test()