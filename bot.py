import telebot
import os
import time

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

def some_function(message):
    # some code here
    handle_order_confirmation(message, file_name, price)

if order_confirmation == "да":
    order_number = len(os.listdir('orders')) + 1
    os.mkdir(f'orders/order_{order_number}')
    with open(f'orders/order_{order_number}/order.txt', 'w') as f:
        f.write(f'Номер заказа: {order_number}\n')
    bot.send_message(message.chat.id, f'Ваш заказ был успешно оформлен. Номер вашего заказа: {order_number}. Сумма к оплате: {price} руб.')
else:
    print('Ваш заказ не был оформлен.')

# Отправляем пользователю информацию о заказе
bot.send_message(message.chat.id, f'Ваш заказ был успешно оформлен. Номер вашего заказа: {order_number}. '
                                  f'Если у вас возникнут вопросы, обращайтесь к нам в любое удобное время!')
