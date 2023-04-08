import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
from PIL import Image
import pytesseract
import PyPDF2
import docx2txt

# функция, которая будет вызываться при получении команды /start
def start(update, context):
    update.message.reply_text('Привет! Я бот, который может распознавать текст на изображении, PDF- и Word-файлах. Пришли мне файл и я скажу тебе, сколько символов в нем!')

from datetime import datetime
import time

from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler, CallbackQueryHandler

# функция, которая будет вызываться при получении изображения
def image(update: Update, context: CallbackContext):
    # получаем файл из сообщения
    photo_file = update.message.photo[-1].get_file()
    # создаем список для хранения фотографий, если его нет
    if 'photos' not in context.chat_data:
        context.chat_data['photos'] = []
    # сохраняем файл во временную директорию с исходным именем файла
    photo_path = f"{photo_file.file_path.split('/')[-1]}"
    photo_file.download(photo_path)
    context.chat_data['photos'].append(photo_path)
    # отправляем сообщение пользователю с исходным названием файла
    update.message.reply_text(f'Фотография {photo_path} добавлена, выполняем расчет')
    # если было загружено несколько фотографий, считаем общее количество символов на всех фотографиях
    if len(context.chat_data['photos']) > 1:
        total_count = 0
        for photo_path in context.chat_data['photos']:
            img = Image.open(photo_path)
            text = pytesseract.image_to_string(img, lang='eng')
            count = len(text)
            total_count += count
        update.message.reply_text(f'На {len(context.chat_data["photos"])} изображениях {total_count} символов')
    # если была загружена только одна фотография, считаем количество символов на ней и отправляем ответ пользователю
    else:
        img = Image.open(context.chat_data['photos'][0])
        text = pytesseract.image_to_string(img, lang='eng')
        count = len(text)
        update.message.reply_text(f'На изображении {count} символов')

    # создаем кнопки и отправляем их пользователю
    keyboard = [
        [InlineKeyboardButton('Добавить еще фотографию документа', callback_data='add_photo')],
        [InlineKeyboardButton('Рассчитать стоимость перевода', callback_data='calculate_translation_price')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите действие:', reply_markup=reply_markup)


# функция для кнопки "Добавить еще фотографию документа"
def add_photo(update: Update, context: CallbackContext):
    # считаем общее количество символов на всех фотографиях
    total_count = 0
    for photo_path in context.chat_data['photos']:
        img = Image.open(photo_path)
        text = pytesseract.image_to_string(img, lang='eng')
        count = len(text)
        total_count += count
# вычисляем стоимость на основе количества символов
    price_per_symbol = 0.01  # цена за один символ (можно заменить на свою)
    price = total_count * price_per_symbol

# отправляем сообщение с результатом в виде ответа на нажатие кнопки
    update.callback_query.answer(f'Стоимость перевода: {price} руб')

# создаем кнопку "Добавить еще фотографию документа"
    add_photo_button = InlineKeyboardButton('Добавить еще фотографию документа', callback_data='add_photo')
# создаем Inline клавиатуру с кнопкой "Добавить еще фотографию документа"
    keyboard = [[add_photo_button]]
    reply_markup = InlineKeyboardMarkup(keyboard)

# отправляем сообщение с новой клавиатурой
    update.callback_query.edit_message_text(text='Выберите действие:', reply_markup=reply_markup)


# функция, которая будет вызываться при получении pdf-файла
from pdf2image import convert_from_path

def pdf(update, context):
    # получаем файл из сообщения
    pdf_file = update.message.document.get_file()
    # сохраняем файл во временную директорию
    pdf_file.download('file.pdf')

    # Отслеживание прогресса
    update.message.reply_text('Начинаю расчет объема вашего PDF-файла...')
    pages = convert_from_path('file.pdf')
    total_pages = len(pages)

    # Конвертация и распознавание текста на каждой странице
    text = ''
    for i, page in enumerate(pages):
        # Конвертация в изображение
        page_image = page.convert('RGB')
        # Распознавание текста на изображении
        text += pytesseract.image_to_string(page_image, lang='eng')
        # Отправка сообщения о прогрессе
        progress = (i+1)
        update.message.reply_text(f'Обработано {progress:.2f} страниц...')

    # считаем количество символов и отправляем ответ пользователю
    count = len(text)
    update.message.reply_text(f'В PDF-файле {count} символов')

# функция, которая будет вызываться при получении файла формата Word
def doc(update, context):
    # получаем файл из сообщения
    doc_file = update.message.document.get_file()
    # сохраняем файл во временную директорию
    doc_file.download('file.docx')
    # открываем файл и распознаем текст
    text = docx2txt.process('file.docx')
    # считаем количество символов и отправляем ответ пользователю
    count = len(text)
    update.message.reply_text(f'В файле формата Word {count} символов')

# функция, которая будет вызываться при получении текстового сообщения
def text(update, context):
    update.message.reply_text('Пожалуйста, отправь мне файл!')

def main():
    # создаем объект бота
    bot = telegram.Bot(token='6225159605:AAHvu7ldYN5tLcHFG56i1Pu1_FQfWa7vxzM')

    # создаем объект для взаимодействия с Telegram API
    global updater
    updater = Updater(bot.token, use_context=True)
    dispatcher = updater.dispatcher

    # создаем обработчики команд и сообщений
    start_handler = CommandHandler('start', start)
    image_handler = MessageHandler(Filters.photo, image)
    pdf_handler = MessageHandler(Filters.document.mime_type('application/pdf'), pdf)
    doc_handler = MessageHandler(Filters.document.mime_type('application/vnd.openxmlformats-officedocument.wordprocessingml.document'), doc)
    text_handler = MessageHandler(Filters.text, text)

    # добавляем обработчики в диспетчер
    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(image_handler)
    updater.dispatcher.add_handler(pdf_handler)
    updater.dispatcher.add_handler(doc_handler)
    updater.dispatcher.add_handler(text_handler)

    # запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
