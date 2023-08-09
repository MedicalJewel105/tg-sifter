"""All parts of the subroutines are called here."""

import database_manager
import post_parser
import forwarder
import post_scrapper
import post_sifter


db = database_manager.database()
channels_data = db.channels
clone_channels_data = db.clone_channels

def main():
    for channel_data in channels_data:
        if not channel_data.is_ok or channel_data.clone_name not in [i.name for i in clone_channels_data]:
            continue
        new_posts, last_post_id, base_post = post_scrapper.scrap_channel(channel_data.name, channel_data.last_post_id)
        posts = post_parser.classify(new_posts)
        
        channel_data.last_post_id = last_post_id
        db.save()

if __name__ == '__main__':
    import logger
    logger.init()
    main()

# TODO: toolbar