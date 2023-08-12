import openai
import telebot
import json
import threading
from chat_gpt import ChatGPT
from time import sleep


class TypingStatus:
    def __init__(self):
        self.statuses = {}

    def set_typing(self, chat_id, status):
        self.statuses[chat_id] = status

    def is_typing(self, chat_id):
        return self.statuses.get(chat_id, False)


def send_chunks(message, text):
    for chunk in [text[i:i + 4096] for i in range(0, len(text), 4096)]:
        bot.reply_to(message, chunk)


with open('config.json', 'r') as file:
    config = json.load(file)

bot_token = config['bot_token']

bot = telebot.TeleBot(bot_token)
chat_gpt = ChatGPT(config)
typing_status = TypingStatus()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! How can I assist you today?")


@bot.message_handler(commands=['clear'])
def clear_conversation(message):
    chat_id = message.chat.id
    chat_gpt.clear_messages(chat_id)
    bot.reply_to(message, "Conversation has been cleared!")


@bot.message_handler(commands=['context'])
def show_context(message):
    chat_id = message.chat.id
    messages = chat_gpt.get_messages(chat_id)
    formatted_messages = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

    if formatted_messages:
        send_chunks(message, formatted_messages)
    else:
        bot.reply_to(message, "No conversation context available.")


@bot.message_handler(commands=['models'])
def list_models(message):
    try:
        models = openai.Model.list()
        model_names = [model['id'] for model in models['data']]
        response = "\n".join(model_names)
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    chat_id = message.chat.id
    user_message = message.text

    typing_status.set_typing(chat_id, True)
    typing_thread = threading.Thread(target=send_typing, args=(chat_id,))
    typing_thread.start()

    response = chat_gpt.receive_message(chat_id, user_message)

    typing_status.set_typing(chat_id, False)
    typing_thread.join()

    send_chunks(message, response)


def send_typing(chat_id):
    while typing_status.is_typing(chat_id):
        bot.send_chat_action(chat_id, 'typing')
        sleep(3)


bot.polling()
