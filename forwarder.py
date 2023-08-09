"""Module with Python bot, which forwards messages to clone channels."""
import post_parser
import logger


def resend(posts: list, clone_name: str) -> None:
    """Resend posts to clone channel."""
    logger.log.write(f'FORWARDER - SENDING MESSAGES TO {clone_name}...')
    # TODO: finish this
    for post in posts:
        print(post.to_json()) # debug
    logger.log.write(f'FORWARDER - SENT {len(posts)} MESSAGES.') # NOTE: needs edits
