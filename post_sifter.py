"""In this module posts are sifted."""
import logger
import database_manager
import filter_library


def sift(posts: list, channel_data: database_manager.channel_data, clone_channel_data: database_manager.clone_channel_data) -> list:
    """Throw away spam configured by channel options."""
    logger.log.write('SIFTER - SIFTING POSTS...')
    sifted_posts = []
    ad_filter = filter_library.FILTER_DICT.get(clone_channel_data.filter, None)
    
    for post in posts:
        print(post.to_json(), end='\n\n')
    print('-----------')

    if ad_filter:
        for content in posts:
            content, is_ad = ad_filter(content, clone_channel_data.spam_match, channel_data.allowed_links)
            if not is_ad:
                if isinstance(content, list):
                    for i in content:
                        sifted_posts.append(i)
                else:
                    sifted_posts.append(content)
        logger.log.write(f'SIFTER - POSTS SIFTED: {len(sifted_posts)} OK, {len(posts) - len(sifted_posts)} SPAM.')
    else:
        logger.log.write('SIFTER - NO FILTER FOR THIS CHANNEL.')
        return posts
    
    for post in sifted_posts:
        print(post.to_json(), end='\n\n')

    return sifted_posts

def group_posts(posts: list) -> list:
    """Create lists with grouped posts in parent list."""
    new_list = []
    post_group = []
    for post in posts:
        if post.is_in_group:
            post_group.append(post)
        elif post_group:
            new_list.append(post)
            post_group = []
        else:
            new_list.append(post)
    return new_list