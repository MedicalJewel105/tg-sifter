"""Module with Python bot, which forwards messages to clone channels."""
import logger
import os
import database_manager
import time
import post_parser
from telegram import InputMediaPhoto, InputMediaVideo, Bot
import requests


POST_DELAY_TIME = 5 # delay between new posts, in seconds. small delay will cause errors
BOT_DATA_FILE = 'bot_data.txt'
BOT_DATA_FOLDER = 'data'
BOT_DATA_PATH = os.path.join(BOT_DATA_FOLDER, BOT_DATA_FILE)


async def resend(posts: list[post_parser.tg_post], clone_channel_data: database_manager.clone_channel_data) -> None:
    """Resend posts to clone channel. If it can't be done for some reason, posts go to cache to be posted later."""
    if clone_channel_data.is_private:
        clone_name = clone_channel_data.private_id
    else:
        clone_name = '@'+clone_channel_data.name
    sent_amount = 0
    if posts:
        logger.log.write(f'FORWARDER - SENDING POSTS TO {clone_channel_data.name}...')
    else:
        logger.log.write('FORWARDER - NO POSTS TO SEND.')
        return
    
    for post in posts:
        if clone_channel_data.cache_options.cache_enabled:
            if clone_channel_data.cache_options.check_is_in_cache(post):
                logger.log.write(f'FORWARDER - POST {post.id} IS IN CACHE.') # do not send as it is marked as duplicate
                continue
            clone_channel_data.cache_options.update_cache(post) # update clone channel's cache
        
        if post.is_in_group and not post.is_head_post: # skip as grouped media is already sent
            continue

        try:
            if post.has_text:
                 async with bot:
                     await bot.send_message(clone_name, post.text)

            if post.is_in_group and post.media:
                to_send_media = []
                for link_with_type in post.media:
                    if link_with_type[1] == 'image':
                        to_send_media.append(InputMediaPhoto(link_with_type[0]))
                    elif link_with_type[1] == 'video':
                        to_send_media.append(InputMediaVideo(link_with_type[0]))
                await bot.send_media_group(chat_id=clone_name, media=to_send_media)
                continue

            if post.has_image:
                async with bot:
                    await bot.send_photo(clone_name, post.image)
            
            elif post.has_video:
                async with bot:
                    await bot.send_video(clone_name, post.video)

        except TimeoutError:
            logger.log.warning('BOT - UNABLE TO SEND POST: TimeoutError.')
        except Exception as e:
            logger.log.error(e)
        else:
            sent_amount += 1

        if posts.index(post) != len(posts) - 1: # do not sleep if it is last message to send
            time.sleep(POST_DELAY_TIME)

    logger.log.write(f'FORWARDER - {sent_amount} OF {len(posts)} POSTS SENT.')

def init() -> bool:
    """Initialize bot. Returns True, if OK."""
    # Load configurations from file:
    if not os.path.exists(BOT_DATA_PATH):
        return False
    global API_TOKEN
    with open(BOT_DATA_PATH, 'r') as f:
        API_TOKEN = f.readline()
    if API_TOKEN:
        logger.log.write('FORWARDER - API TOKEN FOUND.')
        global bot
        bot = Bot(API_TOKEN) # here is bot started
    else:
        logger.log.warning('FORWARDER - API TOKEN NOT FOUND.')
    return bool(API_TOKEN)


def debug():
    """Debug function."""


if __name__ == '__main__':
    debug()