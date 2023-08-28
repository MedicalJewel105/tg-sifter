# TG-Sifter

What is this?
This project aims to give people an ability to surf Telegram without annoying and lewd ads.
Posts from public only (for now) channels are scrapped, parsed, filtered and resent to clone channels.
You can decide on your own what is ad and what is not.

# Structure

`launcher` - launches `main` module every N minutes. Also catches unhandled errors.

`main` - file where the procedure order is written.

`logger` - module for error/warning/info logging.

`database_manager` - module for interaction with .json database.

`post_scrapper` - this module scraps posts from channels through Telegram Web.

`post_parser` - here scrapped posts (html) are parsed and `tg_post` objects created.

`post_sifter` - finds filter for channel from `filter_library` and sifts posts.

`filter_library` - module with hand-written filters. Includes an example of filter and some functions for working with text.

`forwarder` - Telegram bot that sends posts to clone channels.

**Note: since in some channels advertising is similar to spam, the project uses somewhere `ad` and somewhere `spam` names.**

Don't forget to install libraries: `pip install -r requirements.txt`.

# Database 

Here you will find out what and how is stored in database.

`database()` object has some variables:

```py
self.channels = [] # list with channel_data objects
self.clone_channels = {} # dict with clone_channel_data objects. Address like to normal dict: clone_channels['<name>'] or clone_channels.get('<name>', '')
```

Database module has some settings:

```py
DATA_FOLDER # folder where all data is stored
CHANNELS_FILE # name of the file where channels info is stored
CLONE_CHANNELS_FILE # name of the file where clone channels info is stored 
JSON_INDENT  # indent for .json files, can be int | None
```

And one method: `self.save()`

## channel_data format

### As .json file:

```json
[
    {
        "name": "short link without @",
        "last_post_id": int,
        "clone_name": "short link without @",
        "allowed_links": [
            "https://..."
        ]
    }
]
```

You can find out ID of a post in Telegram via copying link to message.
Allowed links are used in `filter_library`. There you can differentiate what is ad and what is not.

### As Python object

This object has some useful variables: 

```py
self.name: str # name of a channel to scrap posts from
self.last_post_id: int # id of last scrapped post
self.clone_name: str # name of the channel to resend to
self.allowed_links: list[str]
self.is_ok: bool # debug variable
```

And also a `to_dict()` method.

## clone_channel_data format

### As .json file:

```json
{
    "clone name without @": {
        "is_private": bool,
        "private_id": str, // only is is_private
        "filter": str,
        "cache_options": {
            "cache_enabled": bool,
            "match_rate": float,
            "cache_size": int,
            "cached_posts": [
                {
                    "id": int,
                    "channel_name": "short link without @",
                    "text": str
                }
            ]
        }
    }
}
```

clone_name - short link of a channel, where posts are resent to.
You can easily find it out by copying link to message from that channel.

 - `is_private` - defines if channel is non-pulic.

   - `private_id` - numerical string. You can find out how to get it [here](https://kerkour.com/telegram-bot-send-messages-to-private-channel#:~:text=Getting%20the%20chat_id%20of%20a%20private%20Telegram%20channel). You can open that link in browser, 'botXXX:YYY' is 'bot<bot_token>'.

 - `filter` - filter from `filter_library`, for example `template`.

 - `cache_options` - settings for cache. Needed to prevent duplicate posts.

   - `match_rate` - float between (0, 1]. Used in `difflib.get_close_matches`.

   - `cache_size` - positive int. Means maximum length of cache (amount of cached posts).

   - `cached_posts` - list with dict type (when loaded) objects.

     - `id` - ID of a post.

     - `channel_name` - name of the channel this post is from.

     - `text` - text of a post.

### As Python object

This object has some useful variables: 

```py
self.name: str # name of the clone channel
self.filter: str # filter from filter_library

self.cache_options.cache_enabled: bool
self.cache_options.match_rate: float
self.cache_options.cache_size: int
self.cache_options.cached_posts: list[dict]
```

And also some methods:

```py
self.to_dict()
self.cache_options.update_cache()
self.cache_options.check_is_in_cache()
```



# Logger

Module for logging errors/warnings and info messages.
Has some settings in it:

```py
LOG_FOLDER: str # folder name for log files
MS_ENABLED: bool # enable/disable milliseconds in log messages
BEEP_ENABLED: bool # enables funny beep sound effects when warnings and errors are logged. Uses winsound module.
```

To use from other modules do:

```py
import logger


logger.init()
logger.log.write(...)
logger.log.warning(...)
logger.log.error(...)
```

Functions:

- `write` - write info message to log.
- `warning` - write warning to log. Use for handled exceptions/problems.
- `error` - write error to log. Use for unhandled exceptions.

# Launcher

Launches `main` module via schedule. Also catches unhandled errors.

# Main

Most likely you don't need to do anything here.
Execution queue:

1. Initialize bot.
2. Go through all channel data values:

    1. Scrap new posts.
    2. Parse posts.
    3. Sift posts.
    4. Resent posts.
    5. Save DB.

# Post Scrapper

Module for scrapping posts from Telegram Web.
Has one setting: `MAX_TRIES`.
`MAX_TRIES` defines how many posts to check to find the last one. This is needed because of post deletion.

*In the future: investigate possibilities of scrapping private channels.*

# Post Parser

Module to parse content from post.

Credit to Steelio for his [Telegram Post Scraper](https://github.com/Steelio/Telegram-Post-Scraper) which I used as a template.

```py
class tg_post:
    self.html # bs4.BeautifulSoap object
    self.id: int # ID of a post
    self.channel_name: str # name of the channel post is from
    self.text: str # text of the post
    self.links: list[list[str, str]] # links in post, format: list[list[link_str, text_str]]
    self.has_text: bool
    self.has_links: bool
    self.media: list[list[str, str]] # media of the post, format: list[list[link_str, type_str]] where type_str can be 'image' or 'video'
    self.image: str # str with link
    self.video: str# str with link
    self.has_media: bool
    self.has_image: bool
    self.has_video: bool
    self.is_in_group: bool = self.check_is_in_group() # checks whether post was sent in a media group or not
    self.grouped_with: list # if post is from media group then there are leashed posts (other posts from a group)
    self.is_head_post: bool # is it the first post in the group
```

Also has `.to_dict()` method.

# Post Sifter

Has one sifting function in it. Launches functions from `filter_library`.

# Filter Library

Module where hand-written functions are stored.

Here is an example:

```py
def anecdote(post: post_parser.tg_post, grouped_with: list[post_parser.tg_post], clone_channel_data: dbm.clone_channel_data, allowed_links: list) -> tuple[post_parser.tg_post, bool]:
    """Spam match variable is not used in this filter."""
    has_bad_links = allowed_links_amount(allowed_links, post.links) != len(post.links)
    has_emoji = emot().emoji(post.text)['flag']

    list_of_requirements = [bool(grouped_with), post.has_image, post.has_video, has_bad_links,  has_emoji]
    do_resend = any(list_of_requirements)
    if not has_bad_links: # if has_bad_links, the following is not needed as it is already marked as ad
        post.text = remove_from_text(post.text, [link_text for _, link_text in post.links])

    return post, do_resend
```

Note that `post, grouped_with, clone_channel_data, allowed_links` arguments are given to this function in `post_sifter` module. This should be enough to sift posts.

Don't forget to add your custom filter to `FILTER_DICT` at the end of the file:

```py
FILTER_DICT = {
    'template': template,
    'anecdote': anecdote
}
```

# Forwarder

Not exactly a good module.
Resents messages. Has some options:

```py
POST_DELAY_TIME # delay between new posts, in seconds. small delay will cause Telegram flood warnings
BOT_DATA_FILE # name of the file with bot's api token
BOT_DATA_FOLDER # name of the folder where file with bot's api token is stored
```

For now bot can't send all types of messages user can.
Make sure bot is an admin of a clone channel.