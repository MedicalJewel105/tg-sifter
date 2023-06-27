"""Module to scrap new posts from TG channel."""

from bs4 import BeautifulSoup as BS
import logger
import requests


MAX_TRIES = 15 # how many posts to check to find the last one (needed because of posts deletion)


def _test():
    """Test function for this module."""
    import database_manager
    db = database_manager.database()
    data = db.channels
    x = data[0]
    posts, last_post_id, base_post = scrap_channel(x.name, x.last_post_id)
    for post in posts:
        print(post)
    print(last_post_id)

def scrap_channel(channel_name: str, last_post_id: int) -> tuple[list, int, BS]:
    """Look for latest posts in a specified channel.
    Returns found posts, last found post ID and BS object of base post.."""
    found_posts = []
    current_try = 0
    last_found_post_id = last_post_id
    current_post_id = last_found_post_id + 1
    deleted_posts = 0

    logger.log.write(f'SCRAPPER - PARSING CHANNEL {channel_name}...')

    base_post_response, got_response = _get_response(f'https://t.me/{channel_name}')
    if not got_response: # if we don't get this, we won't be able to identify found posts
        logger.log.warning('SCRAPPER - UNABLE TO GET BASE POST.')
        return [], last_post_id
    base_post = BS(base_post_response.content, 'html.parser') # dead posts are found by comparing text in them to text in this post (channel description)

    while True:
        url = f'https://t.me/{channel_name}/{current_post_id}'
        r, is_ok = _get_response(url)
        if is_ok:
            post = BS(r.content, 'html.parser')
            is_post_found, base_ok = _validate_post(base_post, post)
            if not base_ok: # if base post in channel is not ok, we won't be able to identify found posts
                break
            if is_post_found:
                last_found_post_id = current_post_id
                current_try = 0
                found_posts.append(post)
            else:
                deleted_posts += 1
        
        current_try += 1
        if current_try > MAX_TRIES:
            break
        current_post_id += 1

    current_post_id -= 1 # somehow it works OK
    deleted_posts -= 1 # because value of this variable is raised by 1 at the end of the loop
    # some log stuff:
    all_posts_amount = current_post_id - MAX_TRIES - last_post_id # posts after last existing post are not counted
    deleted_posts -= MAX_TRIES
    logger.log.write(f'SCRAPPER - {all_posts_amount} POSTS FOUND: {len(found_posts)} EXIST, {deleted_posts} DELETED.')
    logger.log.write(f'SCRAPPER - LAST FOUND POST ID: {last_post_id}.')

    return found_posts, last_found_post_id, base_post

def _get_response(url: str) -> tuple[requests.Response | None, bool]:
    """Handle request errors. Returns Responce object (or None) and OK flag."""
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

def _validate_post(base_post: BS, post: BS) -> tuple[bool, bool]:
    """Make sure that post is 'online' (exists and not deleted).
    Retuns 2 booleans. 1 - is_post_found, 2 - is_base_tag_found."""
    # TODO: be able to differentiate between a post and an image: 
    # https://t.me/oldbutgoldbest/6635?single
    # https://t.me/oldbutgoldbest/6636?single
    # https://t.me/oldbutgoldbest/6637?single
    # this all is one 'post': https://t.me/oldbutgoldbest/6633
    base_meta_tag = base_post.find('meta', attrs={'property': 'og:description'})
    # NOTE: if channel base content is empty, it is not accounted
    if base_meta_tag:
        base_description_content = base_meta_tag.get('content', '')
    else:
        logger.log.warning('SCRAPPER - TAG "og:description" NOT FOUND IN BASE POST.')
        return False, False
    
    post_meta_tag = post.find('meta', attrs={'property': 'og:description'})
    if post_meta_tag:
        post_meta_content = post_meta_tag.get('content', '')
    is_post_found = base_description_content != post_meta_content
    
    return is_post_found, True

if __name__ == '__main__':
    _test()