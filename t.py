import os
import libtorrent as lt
import logging
from telegram import Bot
from telegram import Update
from telegram.ext import Updater
from telegram.ext import CommandHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(bot, update):
    update.message.reply_text("Hi! Use /magnet to start downloading a magnet link.")

def download_torrent(link, bot, chat_id):
    ses = lt.session()
    ses.listen_on(6881, 6891)

    torrent_info = lt.torrent_info(link)
    title = torrent_info.name()
    save_path = os.path.join('/path/to/save/downloaded/files', title)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    params = {
        'save_path': save_path,
        'storage_mode': lt.storage_mode_t(2),
        'paused': False,
        'auto_managed': True,
        'duplicate_is_error': True
    }
    handle = lt.add_magnet_uri(ses, link, params)
    ses.start_dht()

    bot.send_message(chat_id=chat_id, text=f"Downloading metadata for {title}...")
    while (not handle.has_metadata()):
        pass
    bot.send_message(chat_id=chat_id, text=f"Metadata received for {title}!")

    torrent_info = handle.get_torrent_info()
    torrent_file = torrent_info.files()
    size = torrent_info.total_size()

    bot.send_message(chat_id=chat_id, text=f"Starting download for {title}...")
    while (handle.status().state != lt.torrent_status.seeding):
        s = handle.status()

def magnet(bot, update, args):
    if not args:
        update.message.reply_text("Please provide a magnet link.")
        return

    link = args[0]
    chat_id = update.message.chat_id
    download_torrent(link, bot, chat_id)
    update.message.reply_text(f"Download of {link} complete!")

def error(bot, update, error):
    logger.warning(f"Update {update} caused error {error}")

def main():
    token = "6022869666:AAGBLpgMLUnVrZgurGc00qZDjK6IJBgGDT4"
    bot = Bot(token)
    updater = Updater(token)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("magnet", magnet, pass_args=True))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

