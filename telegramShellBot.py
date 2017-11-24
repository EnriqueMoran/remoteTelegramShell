import telebot
from telebot import types

TOKEN = ''

bot = telebot.TeleBot(TOKEN)

__author__ = "EnriqueMoran"

PASSWORD = "pass123" 
USERS = "./users.txt"    # Authorized users list
MARKUP = types.ForceReply(selective = False)



@bot.message_handler(commands=['start'])
def send_welcome(message):
    if checkLogin(USERS, message.chat.id):
        bot.send_message(message.chat.id, "Welcome, use /run to start.")
    else:
        msg = bot.send_message(message.chat.id, "Please log in, insert password.", reply_markup = MARKUP)
        bot.register_next_step_handler(msg, validate)


def validate(message):
    if message.text == PASSWORD:
        bot.send_message(message.chat.id, "Logged in, please use /run to start.")
        register(USERS, message.chat.id)
    else:
        msg = bot.send_message(message.chat.id, "Incorrect user/pasword, try again.", reply_markup = MARKUP)
        bot.register_next_step_handler(msg, validate)


@bot.message_handler(commands=['run'])
@bot.message_handler(func=lambda message: True)
def run(message):
    if checkLogin(USERS, message.chat.id) and message.text == "/run":
        bot.send_message(message.chat.id, "You can write commands now.")
    elif checkLogin(USERS, message.chat.id):
        bot.send_message(message.chat.id, "command")


def register(file, user):
    f = open(file, "w+")
    content = f.readlines()
    content = [x.strip() for x in content]
    if not user in content:
        f.write(str(user) + "\n")
    f.close


def checkLogin(file, login):
    check = False
    with open(file) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        if str(login) in content:
            check = True
    return check



if __name__ == "__main__":

    bot.polling(none_stop = True)