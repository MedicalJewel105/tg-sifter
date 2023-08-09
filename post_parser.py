"""
In this module posts are parsed from html code.
(Html got from https://t.me/{channel_name}/{post_id}?embed=1&mode=tme.)
"""

from bs4 import BeautifulSoup as BS
import logger
import re
import html2text

def _test():
    """Developer function."""
    logger.init()
    import json
    with open('test/multiple_videos.html', 'r', encoding='UTF-8') as f:
        html_str = f.read()
    html = BS(html_str, 'html.parser')
    x = tg_post(html)
    print(json.dumps(x.to_json(), indent=4))

class tg_post:
    def __init__(self, html: BS):
        self.html = html
        self.id: int = self.parse_id()
        self.channel_name: str = self.parse_ch_name()
        self.text: str = self.parse_text()
        self.links: list = self.parse_links() # format: list[list[link_str, text_str]]
        self.image: str = self.parse_image()
        self.video: str = self.parse_video()
        
        self.has_text = bool(self.text)
        self.has_links = bool(self.links)
        self.has_image = bool(self.image) # channel logo image doesn't count
        self.has_video = bool(self.video)
        
        self.is_in_group = self.check_is_in_group()
        
        if self.is_in_group:
            self.grouped_with: list = self.get_leashed_posts()
            self.is_head_post = self.check_is_head_post()
        else:
            self.grouped_with = []
            self.is_head_post = False
        
    def _html_to_text(self, html: str) -> str:
        """Parse text from html."""
        h = html2text.HTML2Text()
        h.body_width = 0  # disable line wrapping
        h.ignore_links = True  # ignore hyperlinks
        h.ignore_emphasis = True  # ignore bold and italic formatting
        h.ignore_images = True  # ignore images
        h.protect_links = True  # protect hyperlinks from being stripped out
        h.unicode_snob = True  # use Unicode characters instead of ASCII
        h.wrap_links = False  # disable link wrapping
        h.wrap_lists = False  # disable list wrapping
        h.decode_errors = 'ignore'  # ignore Unicode decoding errors

        text = h.handle(html)
        text = re.sub(r'\*+', '', text)  # remove asterisks
        text = re.sub(r'^[ \t]*[\\`]', '', text, flags=re.MULTILINE)  # remove leading \ or `
        return text

    def parse_text(self) -> str:
        """Parse text from tg post."""
        return self._html_to_text(str(self.html.find('div', {'class': 'tgme_widget_message_text js-message_text', 'dir': 'auto'})))

    def parse_id(self) -> int:
        """Parse post's ID."""
        div_tag = self.html.find('div', class_='tgme_widget_message text_not_supported_wrap js-widget_message')
        if div_tag:
            str_with_id = div_tag.get('data-post', '')
            id_str = str_with_id.split('/')[1]
            try:
                post_id = int(id_str)
            except ValueError:
                post_id = -1
            return post_id
        return -1

    def parse_ch_name(self) -> str:
        """Parse name of the channel post is from."""
        ch_name = ''
        div_tag = self.html.find('div', class_='tgme_widget_message text_not_supported_wrap js-widget_message')
        if div_tag:
            data_str = div_tag.get('data-post', '')
            ch_name = data_str.split('/')[0]
        return ch_name

    def parse_links(self) -> list:
        """Parse all links and mentions (@) from post."""
        result = []
        if not self.text:
            return []
        to_search_in = self.html.find('div', {'class': 'tgme_widget_message_text js-message_text', 'dir': 'auto'}) # links can be wrapped and be not in text field
        if to_search_in:
            links_html = to_search_in.find_all('a') # <a href="https://t.me/exploitex" target="_blank">@exploitex</a></div>
            if links_html:
                for link_html in links_html:
                    link_data = [link_html.get('href'), link_html.get_text()]
                    result.append(link_data)
        return result
        # not needed because all links in posts are wrapped
        # return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', to_search_in) + [word.strip('\n') for word in self.text.split() if word.strip('\n').startswith('@')]

    def parse_image(self) -> str:
        """Parse image link from post."""
        self._raw_img_list = self.html.find_all('a', {'class': 'tgme_widget_message_photo_wrap'})
        if not self._raw_img_list:
            return ''
        raw_img = self._raw_img_list[0]
        style = raw_img['style']
        match = re.search(r"background-image:url\('(.*)'\)", style)
        if match:
            bg_image_url = match.group(1)
            return bg_image_url
        return ''

    def parse_video(self) -> str:
        """Parse video link from post."""
        self._raw_vid_list = self.html.find_all('div', {'class': 'tgme_widget_message_video_wrap'})
        self._raw_vid_thumb_list= self.html.find_all('a', {'class': 'tgme_widget_message_video_player grouped_media_wrap blured js-message_video_player'})
        if not self._raw_vid_list:
            return ''
        raw_vid = self._raw_vid_list[0].find('video')
        return raw_vid.get('src', '')
    
    def check_is_in_group(self) -> bool:
        """Check if post is in group with other posts."""
        return bool(self.html.find('div', {'class': 'tgme_widget_message_grouped_wrap js-message_grouped_wrap'}))

    def get_leashed_posts(self) -> list:
        """Find id's of posts in current group."""
        post_ids = []
        for i in self._raw_img_list + self._raw_vid_thumb_list:
            id_str = i.get('href', '_/_').split('/')[-1].strip('?single')
            try:
                post_id = int(id_str)
            except ValueError:
                post_id = -1
            post_ids.append(post_id)

        return sorted(post_ids)

    def check_is_head_post(self) -> bool:
        """Returns True if post is first in group of posts."""
        return self.id == self.grouped_with[0]

    def to_json(self) -> dict:
        """Get a dict object ready for JSON conversion."""
        json = {
            'id': self.id,
            'channel_name': self.channel_name,
            'text': self.text,
            'links': self.links,
            'image': self.image,
            'video': self.video,
            'has_text': self.has_text,
            'has_links': self.has_links,
            'has_image': self.has_image,
            'has_video': self.has_video,
            'is_in_group': self.is_in_group,
            'grouped_with': self.grouped_with,
            'is_head_post': self.is_head_post
        }
        return json

def classify(posts: list[BS]) -> list:
    """Turn BS objects into tg_post objects."""
    logger.log.write('PARSER - CLASSIFYING POSTS...')
    classified_posts = [tg_post(post) for post in posts]
    logger.log.write('PARSER - POSTS CLASSIFIED.')
    return classified_posts


if __name__ == '__main__':
    _test()