"""In this module posts are parsed and boolean variables are set."""

from bs4 import BeautifulSoup as BS
import logger

class tg_post:
    def __init__(self, x: BS):
        # TODO
        pass
    def validate_spam(self, channel: str) -> bool:
        """Check whether post is spam or not based on settings from channel_option database."""
        # TODO
        return False
        # сделать "разбаловку спама" - при непрохождении порога спама - отмечается как спам

# soup = get_soup(url)
    # meta_tag = soup.find('meta', attrs={'property': 'og:description'})
    # if meta_tag:
    #     print(meta_tag.get('content', ''))
    # else:
    #     print('Тег <meta> не найден.')
    # write_to_file(html)