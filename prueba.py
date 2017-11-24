import telebot
from telebot import types

TOKEN = ''

bot = telebot.TeleBot(TOKEN)

__author__ = "EnriqueMoran"

PASSWORD = "pass123" 
USERS = "./users.txt"    # Authorized users list



@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ForceReply(selective = False)
    if checkLogin(USERS, message.chat.id):
        bot.send_message(message.chat.id, "Welcome, use /run to start.")
    else:
        bot.send_message(message.chat.id, "Please log in, insert password.", reply_markup = markup)      
        def validate(message):
            if message.text == PASSWORD:
                bot.send_message(message.chat.id, "Logged in, please use /run to start.")
                register(USERS, message.chat.id)
            else:
                bot.send_message(message.chat.id, "Incorrect user/pasword, try again.", reply_markup = markup)


@bot.message_handler(commands=['run'])
#@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if checkLogin(USERS, message.chat.id):
        bot.reply_to(message, message.text)


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