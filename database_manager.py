"""Module to communicate with database."""

from os import path, mkdir
import logger
import json
import post_parser


log = logger.logger()
DATA_FOLDER = 'data'
CHANNELS_FILE = 'channels.json'
CLONE_CHANNELS_FILE = 'clone_channels.json'
JSON_INDENT = 4 # int | None
CHANNELS_PATH = path.join(DATA_FOLDER, CHANNELS_FILE)
CLONE_CHANNELS_PATH = path.join(DATA_FOLDER, CLONE_CHANNELS_FILE)


class channel_data:
    """Class with data for channels, where posts are parsed from."""
    def __init__(self, x: dict):
        self.name = x.get('name', '')
        self.last_post_id = x.get('last_post_id', 0)
        self.clone_name = x.get('clone_name', '')
        self.allowed_links = x.get('allowed_links', [])

        self.is_ok = bool(self.name) and bool(x.get('clone_name', ''))
    
    def to_json(self) -> dict:
        """Transform object into .json format."""
        data = {
            'name': self.name,
            'last_post_id': self.last_post_id,
            'clone_name': self.clone_name,
            'allowed_links': self.allowed_links
            }
        return data

class clone_channel_data:
    """Class with data for clone channels, where parsed posts after sifting are forwarded."""
    def __init__(self, name: str, x: dict):
        self.name = name
        self.filter = x.get('filter', None)
        self.spam_match = x.get('spam_match', 0.8)
        self.cache_options = self.cache_options(x.get('cache_options', {}))

    class cache_options:
        """Class to store clone channel's cache options."""
        def __init__(self, y: dict):
            self.cache_enabled = y.get('cache_enabled', False)
            self.cache_amount = y.get('cache_amount', 10) # determines how many posts are stored in db
            self.cached_posts = y.get('cached_posts', [])
        
        def update_cache(self, content: dict | post_parser.tg_post) -> None:
            """Add new post (as json or tg_post) to cache and remove the oldest (defined by order)."""
            if isinstance(content, post_parser.tg_post):
                content = content.to_json()
            self.cached_posts = [content] + self.cached_posts[:-1]
    
    def to_json(self) -> dict:
        """Transform object into .json format."""
        data = {
            self.name: {
                'filter': self.filter,
                'spam_match': self.spam_match,
                'cache_options': {
                    'cache_enabled': self.cache_options.cache_enabled,
                    'cache_amount': self.cache_options.cache_amount,
                    'cached_posts': self.cache_options.cached_posts if self.cache_options.cache_enabled else [] # we don't store posts if duplicate options are not enabled
                }
            }
        }
        return data

class database:
    def __init__(self):
        self.channels = []
        self.clone_channels = {}
        self.__load()

    def __load(self) -> None:
        """Load .json databases and create channel and clone_channel objects."""
        log.write('DB - LOADING CHANNELS DATA...')
        if not path.exists(CHANNELS_PATH):
            log.write(f'ERROR! {CHANNELS_PATH} FILE NOT FOUND.')
            exit()
        with open(CHANNELS_PATH, 'r') as f:
            data = json.load(f)
        for x in data:
            self.channels.append(channel_data(x))
        log.write('DB - LOADED.')

        log.write('DB - LOADING CLONE CHANNELS DATA...')
        if not path.exists(CLONE_CHANNELS_PATH):
            log.write(f'ERROR! {CLONE_CHANNELS_PATH} FILE NOT FOUND.')
            exit()
        with open(CLONE_CHANNELS_PATH, 'r') as f:
            data = json.load(f)
        for x in data:
            self.clone_channels[x] = clone_channel_data(x, data[x])
        log.write('DB - LOADED.')

    def save(self) -> None:
        """Save database to .json files."""
        log.write('DB - SAVING CHANNELS DATA...')
        if not path.isdir(DATA_FOLDER):
            log.write(f'WARNING! {DATA_FOLDER} FOLDER DOES NOT EXIST.')
            mkdir(DATA_FOLDER)
        
        json_data = [i.to_json() for i in self.channels]
        with open(CHANNELS_PATH, 'w') as f:
            json.dump(json_data, f, indent=JSON_INDENT)
        log.write('DB - SAVED.')

        log.write('DB - SAVING CLONE CHANNELS DATA...')
        json_data_dict = {}
        for i in self.clone_channels.values():
            json_data_dict.update(i.to_json())
        with open(CLONE_CHANNELS_PATH, 'w') as f:
            json.dump(json_data_dict, f, indent=JSON_INDENT)
        log.write('DB - SAVED.')
    
def __test():
    """Developer function."""
    k = database()
    ch_data = k.channels[0]
    print(ch_data.to_json())
    print(k.clone_channels)
    for i in k.clone_channels.values():
        print(i.to_json())
    k.save()

if __name__ == '__main__':
    __test()