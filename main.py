"""All parts of the subroutines are called here."""

import database_manager
import post_parser
import forwarder
import post_scrapper
import post_sifter
import asyncio


db = database_manager.database()
channels_data = db.channels
clone_channels_data = db.clone_channels

def main():
    bot_ok = forwarder.init()
    if not bot_ok: exit() # if bot doesn't work, nothing of the following should be done
    for channel_data in channels_data:
        # skip if there is an error or posts are not sent anywhere
        if not channel_data.is_ok:
            logger.log.warning('MAIN - CHANNEL DATA HAS AN ERROR.')
            continue
        logger.log.write(f'MAIN - PROCESSING CHANNEL @{channel_data.name}...')
        if channel_data.clone_name not in clone_channels_data:
            logger.log.warning(f'MAIN - CLONE CHANNEL NAME "{channel_data.clone_name}" NOT FOUND.')
            continue

        clone_channel_data = clone_channels_data[channel_data.clone_name]
        new_posts, last_post_id = post_scrapper.scrap_channel(channel_data.name, channel_data.last_post_id)
        channel_data.last_post_id = last_post_id
        posts = post_parser.classify(new_posts)
        sifted_posts = post_sifter.sift(posts, channel_data, clone_channel_data)
        asyncio.run(forwarder.resend(sifted_posts, clone_channel_data))
        db.save()

if __name__ == '__main__':
    import logger
    logger.init()
    main()