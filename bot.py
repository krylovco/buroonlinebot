import telegram

bot_token = "6225159605:AAHvu7ldYN5tLcHFG56i1Pu1_FQfWa7vxzM"
bot = telegram.Bot(token=bot_token)

# Send a test message to yourself
bot.send_message(chat_id="472346381", text="Hello from your bot!")
