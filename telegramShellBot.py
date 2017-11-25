import subprocess
import os
import datetime
import telebot
from telebot import types



__author__ = "EnriqueMoran"



TOKEN = ''

bot = telebot.TeleBot(TOKEN)

VERSION = "v0.1_2.3.1"
PASSWORD = "" 
USERS = "/home/pi/Share/users.txt"    # Authorized users list, path must be absolute
LOG = "/home/pi/Share/log.txt"    # Connections and commands log file, path must be absolute
MARKUP = types.ForceReply(selective = False)



@bot.message_handler(commands=['start'])
def send_welcome(message):
    registerLog(LOG, message)
    if checkLogin(USERS, message.chat.id):
        bot.send_message(message.chat.id, "Welcome, use /run to start or /help to view info about avaliable commands.")
    else:
        msg = bot.send_message(message.chat.id, "Please log in, insert password.", reply_markup = MARKUP)
        bot.register_next_step_handler(msg, validate)


def validate(message):
    registerLog(LOG, message)
    if message.text == PASSWORD:
        bot.send_message(message.chat.id, "Logged in, please use /run to start.")
        register(USERS, message.chat.id)
    else:
        msg = bot.send_message(message.chat.id, "Incorrect user/pasword, try again.", reply_markup = MARKUP)
        bot.register_next_step_handler(msg, validate)


def changeDir(message):
    registerLog(LOG, message)
    try:
        os.chdir(message.text)
        bot.send_message(message.chat.id,"Current directory: " + str(os.getcwd()))
    except:
        bot.send_message(message.chat.id,"No such directory.")


@bot.message_handler(commands=['cd'])
def cdCommand(message):
    registerLog(LOG, message)
    if checkLogin(USERS, message.chat.id) and message.text == "/cd":
        bot.send_message(message.chat.id, "Write new directory (only path).")
        bot.register_next_step_handler(message, changeDir)
        

@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Current version: " + VERSION)
    bot.send_message(message.chat.id, "Welcome to telegramShell, this bot allows you to remotely control linux terminal.")
    bot.send_message(message.chat.id, "To change directory use /cd to use the rest of the commands use /run")


@bot.message_handler(commands=['run'])
@bot.message_handler(func=lambda message: True)
def run(message):
    registerLog(LOG, message)
    if checkLogin(USERS, message.chat.id) and message.text == "/run":
        bot.send_message(message.chat.id, "You can write commands now.")
    elif checkLogin(USERS, message.chat.id):
        command = message.text
        try:
            p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, cwd = os.getcwd())
            p.wait()
            (output, err) = p.communicate()
            if not output:
                output = "Command not executed."         
            bot.send_message(message.chat.id, str(output))
        except Exception, e:
            error = "Error ocurred: " + str(e)
            errorType = "Error type: " + str((e.__class__.__name__))
            bot.send_message(message.chat.id, str(error))
            bot.send_message(message.chat.id, str(errorType))


def register(file, user):
    f = open(file, "a+")
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


def registerLog(file, command):
    f = open(file, "a+")
    now = datetime.datetime.now().strftime("%m-%d-%y %H:%M:%S ")
    f.write(now + "[" + str(command.from_user.username) + " (" + str(command.chat.id) + ")] " + str(command.text) + "\n")
    f.close()




if __name__ == "__main__":

    bot.polling(none_stop = True)