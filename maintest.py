import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import os
from PIL import Image
import pytesseract
import PyPDF2
import docx2txt

lang_options = ['русский', 'английский', 'немецкий', 'французский', 'азербайджанский', 'арабский', 'армянский', 'белорусский', 'болгарский', 'боснийский', 'венгерский', 'вьетнамский', 'голландский', 'греческий', 'грузинский', 'дари', 'датский', 'езидский', 'иврит', 'индийский', 'индонезийский', 'испанский', 'испанский (мексиканский)', 'итальянский', 'казахский', 'каталанский', 'киргизский', 'китайский', 'корейский', 'латинский', 'латышский', 'литовский', 'македонский', 'молдавский', 'монгольский', 'немецкий', 'нидерландский', 'норвежский', 'персидский', 'польский', 'португальский', 'пушту', 'румынский', 'русский', 'сербский', 'словацкий', 'словенский', 'таджикский', 'тайский', 'татарский', 'тибетский', 'турецкий', 'туркменский', 'удмуртский', 'узбекский', 'украинский', 'урду', 'фарси', 'финский', 'французский', 'хинди', 'хорватский', 'черногорский', 'чешский', 'шведский', 'эстонский', 'японский']

# Функция, которая будет вызываться при получении команды /start
def start(update, context):
    # Отправляем приветственное сообщение
    update.message.reply_text('Привет! Я бот, который может распознавать текст на изображении, PDF- и Word-файлах. Пришли мне файл и я скажу тебе, сколько символов в нем!')

    # Создаем список списков кнопок с языками для перевода
    buttons = [lang_options[i:i+3] for i in range(0, len(lang_options), 3)]

    # Создаем объект клавиатуры и передаем ему список списков кнопок
    reply_markup = telegram.ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)

    # Отправляем сообщение с запросом языка и клавиатурой
    update.message.reply_text('С какого языка необходимо выполнить перевод?', reply_markup=reply_markup)

# Ожидаем выбора языка и сохраняем его в переменной
def select_language(update, context):
    query = update.callback_query
    lang_from = query.data
    context.user_data['lang_from'] = lang_from
    query.answer()
    # Отправляем сообщение с запросом языка перевода и клавиатурой
    button_list = [[KeyboardButton(lang)] for lang in lang_options]
    reply_markup = ReplyKeyboardMarkup(button_list, resize_keyboard=True, one_time_keyboard=True)
    query.message.reply_text('На какой язык необходимо выполнить перевод?', reply_markup=reply_markup)

# Ожидаем выбора языка перевода и сохраняем его в переменной
def select_target_language(update, context):
    query = update.callback_query
    lang_to = query.data
    context.user_data['lang_to'] = lang_to
    query.answer()
    # Рассчитываем стоимость перевода
    price_per_symbol = 0.5  # цена за один символ перевода в рублях
    text_length = 500  # длина текста, подлежащего переводу
    price = price_per_symbol * text_length

    # Отправляем сообщение с результатами расчета стоимости перевода
    query.message.reply_text(f'Перевод с {context.user_data["lang_from"]} на {context.user_data["lang_to"]} стоит {price} рублей.')

from datetime import datetime
import time

# функция, которая будет вызываться при получении изображения
def image(update, context):
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
        context.chat_data['total_count'] = total_count  # сохраняем значение total_count в данных чата
        update.message.reply_text(f'На {len(context.chat_data["photos"])} изображениях {total_count} символов')
    # если была загружена только одна фотография, считаем количество символов на ней и отправляем ответ пользователю
    else:
        img = Image.open(context.chat_data['photos'][0])
        text = pytesseract.image_to_string(img, lang='eng')
        count = len(text)
        context.chat_data['total_count'] = count  # сохраняем значение total_count в данных чата
        update.message.reply_text(f'На изображении {count} символов')

    # Создаем inline кнопки
    keyboard = [
        [telegram.InlineKeyboardButton("Загрузить еще изображение", callback_data='more_images'),
         telegram.InlineKeyboardButton("Рассчитать стоимость перевода", callback_data='calculate_price')]
    ]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение пользователю с кнопками
    update.message.reply_text('Выберите действие:', reply_markup=reply_markup)


# функция, которая будет вызываться при нажатии на кнопки
def button(update, context):
    query = update.callback_query
    # проверяем, какая кнопка была нажата
    if query.data == 'more_images':
        query.edit_message_text(text='Загрузите еще изображение:')
    elif query.data == 'calculate_price':
        # получаем значение total_count из данных чата
        total_count = context.chat_data.get('total_count')
        if total_count is None:
            # Если значение total_count не было сохранено в данных чата, пересчитываем его по загруженным изображениям
            total_count = 0
            for photo_path in context.chat_data['photos']:
                img = Image.open(photo_path)
                text = pytesseract.image_to_string(img, lang='eng')
                count = len(text)
                total_count += count
            # Сохраняем значение total_count в данных чата, чтобы использовать его в будущем
            context.chat_data['total_count'] = total_count

        # Рассчитываем стоимость перевода и отправляем ее пользователю
        price = total_count / 1800 * 520  # предполагаемая цена - 1 цент за символ
        query.edit_message_text(text=f'Общее количество символов: {total_count}\nПредполагаемая цена перевода: {price:.2f} руб.')

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

def main():
    # создаем объект бота
    bot = telegram.Bot(token='6225159605:AAHvu7ldYN5tLcHFG56i1Pu1_FQfWa7vxzM')

    # создаем объект для взаимодействия с Telegram API
    global updater
    updater = Updater(bot.token, use_context=True)

    # создаем обработчики команд и сообщений
    start_handler = CommandHandler('start', start)
    image_handler = MessageHandler(Filters.photo, image)
    pdf_handler = MessageHandler(Filters.document.mime_type('application/pdf'), pdf)
    doc_handler = MessageHandler(Filters.document.mime_type('application/vnd.openxmlformats-officedocument.wordprocessingml.document'), doc)


    # добавляем обработчики в диспетчер
    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(image_handler)
    updater.dispatcher.add_handler(pdf_handler)
    updater.dispatcher.add_handler(doc_handler)

# Создаем объекты класса CallbackQueryHandler на основе функций select_language и select_target_language
    select_language_handler = CallbackQueryHandler(select_language)
    select_target_language_handler = CallbackQueryHandler(select_target_language)

# Добавляем обработчики в диспетчер
    updater.dispatcher.add_handler(select_language_handler)
    updater.dispatcher.add_handler(select_target_language_handler)

# создаем обработчик для нажатия на кнопки
    button_handler = CallbackQueryHandler(button)
    updater.dispatcher.add_handler(button_handler)

    # запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
