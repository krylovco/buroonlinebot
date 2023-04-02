import telegram

async def main():
    bot_token = '6225159605:AAHvu7ldYN5tLcHFG56i1Pu1_FQfWa7vxzM'
    bot = telebot.TeleBot(bot_token)
    await bot.send_message(chat_id="472346381", text="Hello from your bot!")
