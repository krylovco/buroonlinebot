import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, MessageFilters
from PIL import Image
import pytesseract


TOKEN = 'ваш_токен_бота'

def start(update, context):
    update.message.reply_text('Привет! Отправь мне изображение с текстом, и я посчитаю количество символов на нем.')

def count_chars(update, context):
    # Получение файла из сообщения
    file = context.bot.getFile(update.message.photo[-1].file_id)
    # Скачивание файла
    file.download('image.jpg')
    # Открытие изображения с помощью PIL
    image = Image.open('image.jpg')
    # Распознавание текста на изображении с помощью pytesseract
    text = pytesseract.image_to_string(image, lang='rus')
    # Подсчет количества символов в тексте
    count = len(text)
    # Отправка ответа
    update.message.reply_text(f'Количество символов: {count}')

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(MessageFilters.photo, count_chars))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
