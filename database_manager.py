"""Module to communicate with database."""

from os import path, mkdir
import logger
import json
import post_parser
import difflib


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
        self.name: str = x.get('name', '')
        self.last_post_id: int = x.get('last_post_id', 0)
        self.clone_name: str = x.get('clone_name', '')
        self.allowed_links: list[str] = x.get('allowed_links', [])

        self.is_ok: bool = bool(self.name) and bool(x.get('clone_name', ''))
    
    def to_dict(self) -> dict:
        """Get a dict object ready for JSON conversion."""
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
        self.name: str = name
        self.filter: str = x.get('filter', None)
        self.cache_options = self.cache_options(x.get('cache_options', {}))

    class cache_options:
        """Class to store clone channel's cache options."""
        def __init__(self, y: dict):
            self.cache_enabled: bool = y.get('cache_enabled', False)
            self.match_rate: float = y.get('match_rate', 0.8) # for check in cache function
            self.cache_size: int = y.get('cache_size', 10) # determines how many posts are stored in db
            self.cached_posts: list[dict] = y.get('cached_posts', [])
        
        def update_cache(self, content: dict | post_parser.tg_post) -> None:
            """Add new post (as json or tg_post) to cache and remove the oldest (defined by order)."""
            if isinstance(content, post_parser.tg_post):
                content = content.to_dict(True)
            if len(self.cached_posts) < self.cache_size:
                self.cached_posts.append(content)
            else:
                self.cached_posts = [content] + self.cached_posts[:-1]
            
        def check_is_in_cache(self, post: post_parser.tg_post, match_rate: float = None) -> bool:
            """Check if post is already in cache.
            Can be used to avoid duplicates in clone channels.
            Match rate is usually set in filter library.
            Searches only in text."""
            if not self.cache_enabled:
                logger.log.warning('DB - CACHE IS NOT ENABLED BUT POST IS SEARCHED FOR IN IT.')
                return False
            if match_rate == None:
                match_rate = self.match_rate
            post_text = post.text.replace('\n', '')
            post_texts = [i.get('text', '').replace('\n', '') for i in self.cached_posts]
            return bool(difflib.get_close_matches(post_text, post_texts, cutoff=match_rate))
    
    def to_dict(self) -> dict:
        """Get a dict object ready for JSON conversion."""
        data = {
            self.name: {
                'filter': self.filter,
                'cache_options': {
                    'cache_enabled': self.cache_options.cache_enabled,
                    'match_rate': self.cache_options.match_rate,
                    'cache_size': self.cache_options.cache_size,
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

        log.write('DB - LOADING CLONE CHANNELS DATA...')
        if not path.exists(CLONE_CHANNELS_PATH):
            log.write(f'ERROR! {CLONE_CHANNELS_PATH} FILE NOT FOUND.')
            exit()
        with open(CLONE_CHANNELS_PATH, 'r', encoding='UTF-8') as f:
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
        
        json_data = [i.to_dict() for i in self.channels]
        with open(CHANNELS_PATH, 'w') as f:
            json.dump(json_data, f, indent=JSON_INDENT)

        log.write('DB - SAVING CLONE CHANNELS DATA...')
        json_data_dict = {}
        for i in self.clone_channels.values():
            json_data_dict.update(i.to_dict())
        with open(CLONE_CHANNELS_PATH, 'w', encoding='UTF-8') as f:
            json.dump(json_data_dict, f, indent=JSON_INDENT, ensure_ascii=False)
        
        log.write('DB - SAVED.')
    
def __test():
    """Developer function."""
    from post_parser import tg_post
    from bs4 import BeautifulSoup as BS
    with open('test/video.html', 'r') as f:
        post = tg_post(BS(f.read(), features="html.parser"))
    k = database().clone_channels.get('anekdotsdots')
    print(k.cache_options.check_is_in_cache(post))

if __name__ == '__main__':
    __test()