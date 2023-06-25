"""Module to parse new posts from TG channel."""

from bs4 import BeautifulSoup as BS
import logger
import database_manager
import requests

db = database_manager.database()
data = db.channels
log = logger.logger()
MAX_TRIES = 15 # how many posts to check to find the last one (needed because of posts deletion)


def _test():
    """Test function for this module."""

def parse_channel(channel_data: list) -> tuple[list, int]:
    """Look for latest posts in a specified channel.
    Returns found posts and last found post ID."""
    found_posts = []
    channel_name = channel_data[0]
    last_found_post_id = channel_data[1]
    current_try = 0
    current_post_id = channel_data[1] + 1

    log.write(f'SCRAPPER - PARSING CHANNEL {channel_name}...')

    base_post_response, got_response = get_response(f'https://t.me/{channel_name}')
    if not got_response: # if we don't get this, we won't be able to identify found posts
        log.warning('SCRAPPER - UNABLE TO GET BASE POST.')
        return [], last_found_post_id
    base_post = BS(base_post_response.content, 'html.parser')

    while True:
        url = f'https://t.me/{channel_name}/{current_post_id}'
        r, is_ok = get_response(url)
        if is_ok:
            post = BS(r.content, 'html.parser')
            is_post_found, base_ok = validate_post(base_post, post)
            if not base_ok: # if it is not ok, we won't be able to identify found posts
                break
            if is_post_found:
                last_found_post_id = current_post_id
                current_try = 0
                found_posts.append(post)
        
        current_try += 1
        if current_try > MAX_TRIES:
            break
        current_post_id += 1

        # print(post)
        print('---')
        print(current_post_id)
        print('---')
        print(is_post_found)
        print('---')

    if found_posts:
        text = f'{len(found_posts)} POSTS FOUND'
    else:
        text = 'NO POSTS FOUND'
    log.write(f'SCRAPPER - {text}.')

    return found_posts, last_found_post_id

def get_response(url: str) -> tuple[requests.Response | None, bool]:
    """Handle request errors. Returns Responce object (or None) and OK flag."""
    try:
        r = requests.get(url)
    except requests.exceptions.Timeout:
        log.warning('SCRAPPER - TIMEOUT ERROR.')
    except requests.exceptions.ConnectionError:
        log.warning('SCRAPPER - CHECK CONNECTION.')
    except Exception as e:
        log.error(e)
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
        log.warning(error)
    return None, False

def validate_post(base_post: BS, post: BS) -> tuple[bool, bool]:
    """Make sure that post is 'online' (exists and not deleted).
    Retuns 2 booleans. 1 - is_post_found, 2 - is_base_tag_found."""
    base_meta_tag = base_post.find('meta', attrs={'property': 'og:description'})
    # NOTE: if content is empty, it is not accounted.
    if base_meta_tag:
        base_description_content = base_meta_tag.get('content', '')
    else:
        log.warning('SCRAPPER - TAG "og:description" NOT FOUND IN BASE POST.')
        return False, False
    
    post_meta_tag = post.find('meta', attrs={'property': 'og:description'})
    # print(post_meta_tag) # DEBUG
    if post_meta_tag:
        post_meta_content = post_meta_tag.get('content', '')
    is_post_found = base_description_content != post_meta_content
    
    return is_post_found, True

if __name__ == '__main__':
    _test()