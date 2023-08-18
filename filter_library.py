"""Library with post filters."""
import post_parser
import database_manager as dbm
from emot.core import emot


def template(post: post_parser.tg_post, grouped_with: list[post_parser.tg_post], clone_channel_data: dbm.clone_channel_data, allowed_links: list) -> tuple[post_parser.tg_post, bool]:
    """Returns modified (or not) post and flag to resend it or not."""
    return post, True

def anecdote(post: post_parser.tg_post, grouped_with: list[post_parser.tg_post], clone_channel_data: dbm.clone_channel_data, allowed_links: list) -> tuple[post_parser.tg_post, bool]:
    """Spam match variable is not used in this filter."""
    has_bad_links = allowed_links_amount(allowed_links, post.links) != len(post.links)
    has_emoji = emot().emoji(post.text)['flag']

    list_of_requirements = [bool(grouped_with), post.has_image, post.has_video, has_bad_links,  has_emoji]
    do_resend = any(list_of_requirements)
    if not has_bad_links: # if has_bad_links, the following is not needed as it is already marked as ad
        post.text = remove_from_text(post.text, [link_text for _, link_text in post.links])

    return post, do_resend


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
    'template': template,
    'anecdote': anecdote
}

