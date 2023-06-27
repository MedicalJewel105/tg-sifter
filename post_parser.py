"""In this module posts are parsed and boolean variables are set."""

from bs4 import BeautifulSoup as BS
import logger
import database_manager


def _test():
    """Developer function."""
    db = database_manager.database()
    data = db.channels


def classify(posts: list, base_post: BS) -> list:
    """Turn BS objects into tg_post objects."""
    logger.log.write('PARSER - CLASSIFYING POSTS...')
    classified_base_post = tg_post(base_post)
    classified_posts = []
    for post in posts:
        classified_post = tg_post(post)
        # some variables setting
    logger.log.write('PARSER - POSTS CLASSIFIED.')
    return classified_posts

class tg_post:
    def __init__(self, html: BS):
        self.text = self.parse_text()
        self.links = self.parse_links()
        self.image = self.parse_image()
        self.video = self.parse_video()
        self.button = []
        self.poll = '' # placeholder
        self.id: int # TODO
        
        self.has_text: bool = bool(self.text)
        self.has_links: bool
        self.has_image: bool
        self.image_equals_logo: bool
        self.has_video: bool
        self.has_poll: bool
        self.has_button: bool # (?)
    
    def parse_links(self) -> list:
        """Parse all links from post."""
        if not self.text:
            return []

    def parse_image(self) -> str:
        """Parse image link from post."""

    def parse_video(self) -> str:
        """Parse video link from post."""

    def parse_text(self) -> str:
        """Parse text from post."""
        meta_tag = self.html.find('meta', attrs={'property': 'og:description'})
        if meta_tag:
            text = meta_tag.get('content', '')
            return text
        logger.log.warning(f'PARSER - UNABLE TO PARSE TEXT [POST ID: {self.id}].')
        return ''
    
    def to_readable(self):
        """Get a ready-to-send message."""

# add later:
# soup = get_soup(url)
# meta_tag = soup.find('meta', attrs={'property': 'og:description'})
# if meta_tag:
#     print(meta_tag.get('content', ''))
# else:
#     print('Тег <meta> не найден.')
# write_to_file(html)

def sift(posts: list, channel_data: database_manager.channel_data) -> list:
    """Throw away spam configured by channel options."""
    logger.log.write('PARSER - SIFTING POSTS...')

    logger.log.write('PARSER - POSTS SIFTED: {} OK, {} SPAM.')

    return []



if __name__ == '__main__':
    _test()