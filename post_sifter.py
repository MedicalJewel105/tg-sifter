import logger
import database_manager


def sift(posts: list, channel_data: database_manager.channel_data) -> list:
    """Throw away spam configured by channel options."""
    logger.log.write('PARSER - SIFTING POSTS...')
    sifted_posts = []

    logger.log.write('PARSER - POSTS SIFTED: {} OK, {} SPAM.')

    return sifted_posts