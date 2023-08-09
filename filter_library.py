"""Library with post filters."""
import post_parser


def template(post: list | post_parser.tg_post, spam_match: float, allowed_links: list) -> tuple[list | post_parser.tg_post, bool]:
    """Returns modified (or not) post and flag if it is ad or not."""
    is_grouped = isinstance(post, list)


def anecdote(post: list | post_parser.tg_post, spam_match: float, allowed_links: list) -> tuple[list | post_parser.tg_post, bool]:
    """Spam match variable is not used in this filter."""
    is_grouped = isinstance(post, list)
    is_ad = True if is_grouped else post.has_image or post.has_links
    return post, is_ad

FILTER_DICT = {
    'anecdote': anecdote
}