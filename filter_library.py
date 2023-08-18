"""Library with post filters."""
import post_parser
import database_manager as dbm
from emot.core import emot


def template(post: post_parser.tg_post, grouped_with: list[post_parser.tg_post], clone_channel_data: dbm.clone_channel_data, allowed_links: list) -> tuple[post_parser.tg_post, bool]:
    """Returns modified (or not) post and flag to resend it or not."""
    return post, True

def allowed_links_amount(allowed_links: list, post_links: list) -> int:
    """Get amount of allowed links that are found in post links."""
    return len([link for link, link_text in post_links if link in allowed_links])

def remove_from_text(text: str, to_remove: list[str]) -> str:
    """Returns new post text without specified text."""
    for content in to_remove:
        if isinstance(content, list): # incorrect usage
            return text
        text = text.replace(content, '')
        text = text.strip()
        text = text.strip('\n')

    return text

FILTER_DICT = {
    'template': template
}

