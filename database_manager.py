"""Module to communicate with database."""

from os import path, mkdir
import logger
import json


log = logger.logger()
DATA_FOLDER = 'data'
CHANNELS_FILE = 'channels.json'
CHANNELS_PATH = path.join(DATA_FOLDER, CHANNELS_FILE)


class channel_data:
    def __init__(self, x: dict):
        self.name = x.get('name', '')
        self.last_post_id = x.get('last_post_id', 0)
        self.clone_name = x.get('clone_name', '')
        self.spam_options = self._spam_options(x.get('spam_options', {}))
        self.duplicate_options = self._duplicate_options(x.get('duplicate_options', {}))

        self.is_ok = bool(self.name) and bool(x.get('spam_options', {})) and bool(x.get('duplicate_options', {})) and bool(x.get('clone_name', ''))

    class _spam_options:
        """Class to store channel spam options."""
        def __init__(self, y: dict):
            self.has_link = y.get('has_link', None)
            self.has_image = y.get('has_image', None)
            self.has_video = y.get('has_video', None)
            self.has_poll = y.get('has_poll', None)
            self.has_text = y.get('has_text', None)
            self.has_button = y.get('has_button', None)
            self.allowed_links = y.get('allowed_links', [])
            self.spam_match = y.get('spam_match', 0.8)

    class _duplicate_options:
        """Class to store channel posts duplication options."""
        def __init__(self, z: dict):
            self.is_enabled = z.get('is_enabled', False)
            self.cache_amount = z.get('cache_amount', 10) # determines how many posts are stored in db
            self.cached_posts = z.get('cached_posts', [])
        
        def update_cache(self, content) -> None:
            """Add new post to cache and remove the oldest (defined by order)."""
            self.cached_posts = [content] + self.cached_posts[:-1]
    
    def to_json(self) -> dict:
        """Transform object into .json format."""
        data = {
            'name': self.name,
            'last_post_id': self.last_post_id,
            'clone_name': self.clone_name,
            'spam_options': {
                'has_link': self.spam_options.has_link,
                'has_image': self.spam_options.has_image,
                'has_video': self.spam_options.has_video,
                'has_poll': self.spam_options.has_poll,
                'has_text': self.spam_options.has_text,
                'has_button': self.spam_options.has_button,
                'spam_match': self.spam_options.spam_match,
                'allowed_links': self.spam_options.allowed_links
            },
            'duplicate_options': {
                'is_enabled': self.duplicate_options.is_enabled,
                'cache_amount': self.duplicate_options.cache_amount,
                'cached_posts': self.duplicate_options.cached_posts if self.duplicate_options.is_enabled else [] # we don't store posts if duplicate options are not enabled
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
    ch_data = k.channels[0]
    print(ch_data.to_json())
    k.save()

if __name__ == '__main__':
    __test()