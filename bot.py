import telebot
import os

bot = telebot.TeleBot("YOUR_TOKEN_HERE")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Добрый день! Я бот-менеджер бюро переводов. Я смогу рассчитать стоимость вашего заказа и помочь в его оформлении.")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "Чтобы рассчитать стоимость заказа, загрузите документ или изображение и следуйте инструкциям.")

@bot.message_handler(content_types=['document', 'photo'])
def handle_docs_photo(message):
    chat_id = message.chat.id
    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = file_info.file_path.split('/')[-1]

    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    bot.reply_to(message, "Файл успешно загружен. Будут ли еще страницы этого документа?")
    bot.register_next_step_handler(message, handle_additional_pages, file_name)

def handle_additional_pages(message, file_name):
    additional_pages = message.text.lower()
    if additional_pages == "да":
        bot.reply_to(message, "Отлично, загрузите еще страницы.")
        bot.register_next_step_handler(message, handle_docs_photo)
    else:
        bot.reply_to(message, "Будут ли еще другие документы для перевода?")
        bot.register_next_step_handler(message, handle_additional_docs, file_name)

def handle_additional_docs(message, file_name):
    additional_docs = message.text.lower()
    if additional_docs == "да":
        bot.reply_to(message, "Отлично, загрузите следующий документ.")
        bot.register_next_step_handler(message, handle_docs_photo)
    else:
        with open(file_name, 'r', encoding='utf-8') as f:
            file_content = f.read()
            symbols_count = len(file_content)

        price = round(symbols_count / 1800 * 580, 2)

        bot.reply_to(message, f"Объем документа: {symbols_count} символов. Ориентировочная стоимость услуги: {price} руб.")
        bot.reply_to(message, "Желаете оформить заказ?")
        bot.register_next_step_handler(message, handle_order_confirmation, file_name, price)

def handle_order_confirmation(message, file_name, price):
    order_confirmation = message.text.lower()
    if order_confirmation == "да":
        order_number = len(os.listdir('orders')) + 1
        os.mkdir(f'orders/order_{order_number}')

        with open(f'orders/order_{order_number}/{file_name}', 'wb') as new_file:
            with open(file_name, 'rb') as f:
                new_file.write(f.read())

        bot.reply_to(message, "Введите адрес электронной почты:")
        bot.register_next_step_handler(message, handle_email, order_number, price)
    else:
        bot.reply_to(message, "Спасибо, что Вы выбрали опцию: нет, других документов для перевода у нас нет.")
# Рассчитываем ориентировочную стоимость второго документа
        second_doc_price = second_doc_length // 1800 * 580
        bot.reply_to(message, f"Ориентировочная стоимость услуги для второго документа: {second_doc_price} руб.")

        # Запрашиваем желание клиента оформить заказ
        msg = bot.reply_to(message, "Желаете оформить заказ? (Да/Нет)")
        bot.register_next_step_handler(msg, process_order_confirmation, first_doc_price, second_doc_price, order_folder_path)

except Exception as e:
    bot.reply_to(message, 'Ошибка сервера, попробуйте еще раз позже')
    def process_order_confirmation(message, first_doc_price, second_doc_price, order_folder_path):
try:
confirmation = message.text.lower()
if confirmation == "да":
order_num = len(os.listdir(order_folder_path)) + 1
order_folder = os.path.join(order_folder_path, f"Order_{order_num}")
os.makedirs(order_folder)
 bot.reply_to(message, "Отлично! Для оформления заказа, мне необходимо получить дополнительную информацию.")

        # Запрашиваем данные клиента
        msg = bot.reply_to(message, "Введите Ваш адрес электронной почты")
        bot.register_next_step_handler(msg, process_order_email, order_folder, first_doc_price, second_doc_price)

    elif confirmation == "нет":
        bot.reply_to(message, "Спасибо за использование нашего бота!")
    else:
        bot.reply_to(message, "Пожалуйста, ответьте 'Да' или 'Нет'.")

except Exception as e:
    bot.reply_to(message, 'Ошибка сервера, попробуйте еще раз позже')
def process_order_email(message, order_folder, first_doc_price, second_doc_price):
try:
email = message.text
msg = bot.reply_to(message, "Введите Ваш номер телефона")
bot.register_next_step_handler(msg, process_order_phone, order_folder, first_doc_price, second_doc_price, email)
except Exception as e:
bot.reply_to(message, 'Ошибка сервера, попробуйте еще раз позже')
def process_order_phone(message, order_folder, first_doc_price, second_doc_price, email):
try:
phone = message.text
msg = bot.reply_to(message, "Введите Ваше ФИО на иностранном языке")
bot.register_next_step_handler(msg, process_order_name, order_folder, first_doc_price, second_doc_price, email, phone)
except Exception as e:
bot.reply_to(message, 'Ошибка сервера, попробуйте еще раз позже')
def process_order_name(message, order_folder, first_doc_price, second_doc_price, email, phone):
try:
name = message.text
order_file_path = os.path.join(order_folder, "order.txt")
 with open(order_file_path, "w") as f:
    f.write(f"Адрес электронной почты: {client_email}\n")
    f.write(f"Номер телефона: {client_phone}\n")
    f.write(f"ФИО на иностранном языке: {client_name}\n")
    f.write(f"Номер заказа: {order_num}\n")
    f.write(f"Общая стоимость: {total_cost} руб.\n")
    f.write(f"Статус заказа: В ожидании подтверждения\n")
# Формируем заказ
    order = f"""Новый заказ!\n
    Заказ №{order_number}\n
    Контакты клиента:\n
    ФИО: {client_name}\n
    E-mail: {client_email}\n
    Телефон: {client_phone}\n
    Стоимость: {order_cost} руб.\n
    """
    
    # Отправляем заказ секретарю переводчиков в телеграмм
    bot.send_message(secretary_chat_id, order)
    
    # Оповещаем клиента о номере заказа и что секретарь переводчик свяжется с ним для подтверждения заказа
    bot.reply_to(message, f"Спасибо за заказ! Номер заказа: {order_number}.\n\
    Наш секретарь переводчик свяжется с вами для подтверждения заказа.")
