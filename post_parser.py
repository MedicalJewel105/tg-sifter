"""In this module posts are parsed and boolean variables are set."""

from bs4 import BeautifulSoup as BS
import logger
import database_manager
import re


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
        # some variables setting:
        classified_post.has_image = (classified_post.image != classified_base_post.image)
        
        classified_posts.append(classified_post)
    logger.log.write('PARSER - POSTS CLASSIFIED.')
    return classified_posts

class tg_post:
    def __init__(self, html: BS):
        self.id = self.parse_id()
        self.text = self.parse_text() # TODO
        self.links = self.parse_links()
        self.image = self.parse_image() # TODO
        self.video = self.parse_video() # TODO
        self.button = [] # TODO
        self.poll = '' # placeholder # TODO
        
        self.has_text: bool = bool(self.text)
        self.has_links = bool(self.links)
        self.has_image: bool # channel logo image doesn't count
        self.image_equals_logo: bool  # TODO
        self.has_video: bool  # TODO
        self.has_poll: bool  # TODO
        self.has_button: bool # (?)  # TODO
    
    def parse_id(self) -> int:
        """Parse post's ID."""
        share_specs = ['al:ios:url', 'al:android:url', 'apple-itunes-app']
        post_id = ''
        for app_spec in share_specs:
            if not post_id:
                meta_tag = self.html.find('meta', attrs={'property': app_spec})
                if meta_tag:
                    str_with_id = meta_tag.get('content', '')
                    if str_with_id and (flag_pos := str_with_id.find('post=') != -1):
                        str_id = str_with_id[flag_pos+len('post='):]
                        try:
                            post_id = int(str_id)
                        except ValueError:
                            pass # we'll try to parse it from other fields
        if not post_id:
            post_id = -1 # some flag of error
        return post_id

    def parse_links(self) -> list:
        """Parse all links from post."""
        if not self.text:
            return []
        return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', self.text)

    def parse_image(self) -> str:
        """Parse image link from post."""
        img_link = ''
        meta_tag = self.html.find('meta', attrs={'property': 'og:image'})
        if meta_tag:
            img_link = meta_tag.get('content', '')
        return img_link        

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


def sift(posts: list, channel_data: database_manager.channel_data) -> list:
    """Throw away spam configured by channel options."""
    logger.log.write('PARSER - SIFTING POSTS...')
    sifted_posts = []

    logger.log.write('PARSER - POSTS SIFTED: {} OK, {} SPAM.')

    return sifted_posts


if __name__ == '__main__':
    _test()