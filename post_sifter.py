"""In this module posts are sifted."""
import logger
import database_manager
import filter_library


def sift(posts: list, channel_data: database_manager.channel_data, clone_channel_data: database_manager.clone_channel_data) -> list:
    """Throw away spam configured by channel options."""
    if posts:
        logger.log.write('SIFTER - SIFTING POSTS...')
    else:
        logger.log.write('SIFTER - NO POSTS TO SIFT.')
        return []
    sifted_posts = []
    ad_filter = filter_library.FILTER_DICT.get(clone_channel_data.filter, None)

    if ad_filter:
        for post in posts:
            grouped_posts = get_grouped_posts(post.grouped_with, posts)
            post, is_ad = ad_filter(post, grouped_posts, clone_channel_data, channel_data.allowed_links)
            if not is_ad:
                sifted_posts.append(post)
        logger.log.write(f'SIFTER - POSTS SIFTED: {len(sifted_posts)} OK, {len(posts) - len(sifted_posts)} SPAM.')
    else:
        logger.log.write('SIFTER - NO FILTER FOR THIS CHANNEL.')
        return posts

    return sifted_posts

def get_grouped_posts(grouped_ids: list, posts: list) -> list:
    """Returns objects of posts, which are grouped with current post."""
    if not grouped_ids: return []
    return [i for i in posts if i.id in grouped_ids]