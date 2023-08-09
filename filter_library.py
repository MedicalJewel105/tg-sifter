"""Library with post filters."""
import post_parser


def anecdote(post: post_parser.tg_post, spam_match) -> tuple[post_parser.tg_post, bool]:
    """Returns modified (or not) post and flag if it is ad or not."""
    spam_match_value = 0

    spam_match_value += 0.8


FILTER_LIST = {
    'anecdote': anecdote
}