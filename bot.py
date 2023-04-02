import telegram
from telegram.ext import Updater, CommandHandler

def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text='Hello, I am your bot!')

def main():
    bot_token = '6225159605:AAHvu7ldYN5tLcHFG56i1Pu1_FQfWa7vxzM'
    updater = Updater(bot_token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
