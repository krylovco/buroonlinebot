import os
from io import BytesIO
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from PIL import Image
from PyPDF2 import PdfFileReader
import docx

rrrrtr
# Функция для расчета количества символов в изображении
def count_characters_in_image(image_file):
    with Image.open(image_file) as img:
        text = pytesseract.image_to_string(img)
    return len(text.strip())

# Функция для расчета количества символов в PDF
def count_characters_in_pdf(pdf_file):
    with open(pdf_file, 'rb') as f:
        pdf = PdfFileReader(f)
        num_pages = pdf.getNumPages()
        total_characters = 0
        for i in range(num_pages):
            page = pdf.getPage(i)
            text = page.extractText()
            total_characters += len(text.strip())
    return total_characters

# Функция для расчета количества символов в документе Word
def count_characters_in_docx(docx_file):
    doc = docx.Document(docx_file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return len(' '.join(full_text))


# Обработчик команды /start
def start_handler(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот для расчета количества символов в файлах.")

# Обработчик сообщений с файлами
def file_handler(update: Update, context):
    # Получаем информацию о файле
    file_id = update.message.document.file_id
    file_name = update.message.document.file_name
    file_size = update.message.document.file_size

    # Скачиваем файл
    file_data = BytesIO()
    update.message.document.get_file().download(out=file_data)
    file_data.seek(0)

    # Расчитываем количество символов в файле
    if file_name.endswith('.pdf'):
        num_characters = count_characters_in_pdf(file_data)
    elif file_name.endswith('.docx'):
        num_characters = count_characters_in_docx(file_data)
    elif file_name.endswith('.jpg') or file_name.endswith('.jpeg') or file_name.endswith('.png'):
        num_characters = count_characters_in_image(file_data)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Извините, я не могу обработать этот тип файла.")
        return

    # Отправляем сообщение с результатом
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Файл {file_name} содержит {num_characters} символов.")


def main():
    # Получаем токен из переменной окружения
    token = os.environ.get('TELEGRAM_BOT_TOKEN')

    # Создаем объект updater и передаем ему токен
    updater = Updater(token, use_context=True)

    # Получаем объект dispatcher для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Регистрируем обработчики команд
    dispatcher.add_handler(CommandHandler('start', start_handler))

    # Регистрируем обработчик сообщений с файлами
    dispatcher.add_handler(MessageHandler(Filters.document, file_handler))

    # Запускаем бота
    updater
