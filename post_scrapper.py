"""Module to scrap new posts from TG channel."""

from bs4 import BeautifulSoup as BS
import html2text
import logger
import requests
import re


MAX_TRIES = 15 # how many posts to check to find the last one (needed because of posts deletion)


def _test():
    """Test function for this module."""
    logger.init()
    import database_manager
    db = database_manager.database()
    data = db.channels
    x = data[0]
    posts, last_post_id, _ = scrap_channel(x.name, x.last_post_id)
    for post in posts:
        # print(post)
        pass
    print(last_post_id)

def scrap_channel(channel_name: str, last_post_id: int) -> tuple[list, int]:
    """Look for latest posts in a specified channel.
    Returns found posts, last found post ID and BS object of base post.."""
    found_posts = []
    current_try = 0
    last_found_post_id = last_post_id
    current_post_id = last_found_post_id + 1
    deleted_posts = 0

    logger.log.write('SCRAPPER - PARSING CHANNEL...')

    base_post_response, base_post_ok = _get_response(f'https://t.me/{channel_name}')
    if not base_post_ok: # connection error
        logger.log.warning('SCRAPPER - UNABLE TO GET BASE POST.')
        return [], last_post_id

    while True:
        url = f'https://t.me/{channel_name}/{current_post_id}?embed=1&mode=tme'
        r, is_ok = _get_response(url)
        if is_ok:
            post_html = BS(r.text, 'html.parser')
            is_post_found = _validate_post(post_html)
            if is_post_found:
                last_found_post_id = current_post_id
                current_try = 0
                found_posts.append(post_html)
            else:
                deleted_posts += 1
        
        current_try += 1
        if current_try > MAX_TRIES:
            break
        current_post_id += 1

    # some logging stuff:
    all_posts_amount = current_post_id - MAX_TRIES - last_post_id # posts after last existing post are not counted
    deleted_posts -= MAX_TRIES
    if deleted_posts == all_posts_amount == 1: # somehow it works now
        deleted_posts = all_posts_amount = 0
    logger.log.write(f'SCRAPPER - {all_posts_amount} POSTS FOUND: {len(found_posts)} EXIST, {deleted_posts} DELETED.')
    logger.log.write(f'SCRAPPER - LAST FOUND POST ID: {last_found_post_id}.')
    # note that post with last_post_id was taken into account in previous run

    return found_posts, last_found_post_id

def scrap_private_channel(last_post_id: int) -> tuple[list, int]:
    # TODO: finish this
    pass

def _get_response(url: str) -> tuple[requests.Response | None, bool]:
    """Handle request errors. Returns Response object (or None) and OK flag."""
    try:
        r = requests.get(url)
    except requests.exceptions.Timeout:
        logger.log.warning('SCRAPPER - TIMEOUT ERROR.')
    except requests.exceptions.ConnectionError:
        logger.log.warning('SCRAPPER - CHECK CONNECTION.')
    except Exception as e:
        logger.log.error(e)
    else:
        is_ok = r.status_code == 200
        if is_ok:
            return r, is_ok
        # some error logging:
        bad_codes = {
            "404": "SCRAPPER - PAGE NOT FOUND.",
            "500": "SCRAPPER - INTERNAL SERVER ERROR.",
            "503": "SCRAPPER - SERVICE UNAVAILABLE.",
            "other": f"SCRAPPER - UNKNOWN STATUS CODE: {r.status_code}."
        }
        error = bad_codes.get(r.status_code, "other")
        logger.log.warning(error)
    return None, False

def _validate_post(post_html: BS) -> bool:
    """Make sure that post is 'online' (exists and not deleted).
    Returns True if post is found."""
    
    def _html_to_text(html):
        """Returns text of the post."""
        h = html2text.HTML2Text()
        h.decode_errors = 'ignore'  # ignore Unicode decoding errors
        text = h.handle(html)
        text = re.sub(r'\*+', '', text)  # remove asterisks
        text = re.sub(r'^[ \t]*[\\`]', '', text, flags=re.MULTILINE)  # remove leading \ or `
        return text

    content = _html_to_text(str(post_html.find('div', {'class': 'tgme_widget_message_text js-message_text', 'dir': 'auto'})))
    return content.strip() != 'None'

if __name__ == '__main__':
    _test()