import subprocess
import os
import datetime
import hashlib
import telebot
import time
from telebot import types



__author__ = "EnriqueMoran"



TOKEN = None
VERSION = None
PASSWORD = None
USERS = None    # users.txt path
LOG = None    # log.txt path
SHAREFOLDER = None    # currently working on Linux
LOGLIMIT = None    # max number of lines allowed
APP = None    # currently working app is Telegram
FORBIDDENCOMMANDS = ["wait", "exit", "clear", "aptitude", "raspi-config", "nano", "dc", "htop", "ex", "expand", "vim", "man", "apt-get", "poweroff", "reboot", "ssh", "scp", "wc"]    # non working commands


def loadConfig(configFile):
    global VERSION, TOKEN, PASSWORD, USERS, LOG, LOGLIMIT, ROOT, SHAREFOLDER, APP

    file = open(configFile, "r")
    temp = file.read().splitlines()
    cont = 0
    read = False

    for line in temp:
        if cont == 5 and line[:1] != "" and read == True:
            APP = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 8 and line[:1] != "" and read == True:
            SHAREFOLDER = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 10 and line[:1] != "" and read == True:
            VERSION = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 11 and line[:1] != "" and read == True:
            TOKEN = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 14 and line[:1] != "" and read == True:
            PASSWORD = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 18 and line[:1] != "" and read == True:
            USERS = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 21 and line[:1] != "" and read == True:
            LOG = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 21 and line[:1] != "" and read == True:
            LOGLIMIT = int([file.strip() for file in line.split('=')][1])
            read = False
        if cont == 25 and line[:1] != "" and read == True:
            ROOT = bool([file.strip() for file in line.split('=')][1])
            read = False
        if line[:1] == "#":
            cont += 1
            read = True

configPath = os.getcwd() + "/config.txt"
loadConfig(configPath)

f1 = open(LOG, "a+")
f1.close
f2 = open(USERS, "a+")
f2.close

bot = telebot.TeleBot(TOKEN)
MARKUP = types.ForceReply(selective = False)



@bot.message_handler(commands = ['start'])
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


def install(message):    # install a package
    registerLog(LOG, message)
    try:
        if checkLogin(USERS, message.chat.id):
            package = message.text
            proc = subprocess.Popen('sudo apt-get install -y ' + package, shell = True, stdin = None, stdout = subprocess.PIPE, executable = "/bin/bash")
            
            while True:
                output = proc.stdout.readline()
                if output == '' and proc.poll() is not None:
                    break
                if output:
                    bot.send_message(message.chat.id, output.strip())
            proc.wait()

            if proc.poll() == 0:
                bot.send_message(message.chat.id, package + " sucessfully installed.")
            else:
                bot.send_message(message.chat.id, package + " not installed")
    except Exception as e:
        error = "Error ocurred: " + str(e)
        errorType = "Error type: " + str((e.__class__.__name__))
        bot.send_message(message.chat.id, str(error))
        bot.send_message(message.chat.id, str(errorType))


def uninstall(message):    # uninstall a package
    registerLog(LOG, message)
    try:
        if checkLogin(USERS, message.chat.id):
            package = message.text
            proc = subprocess.Popen('sudo apt-get --purge remove -y ' + package, shell = True, stdin = None, stdout = subprocess.PIPE, executable = "/bin/bash")
            
            while True:
                output = proc.stdout.readline()
                if output == '' and proc.poll() is not None:
                    break
                if output:
                    bot.send_message(message.chat.id, output.strip())
            proc.wait()
            
            if proc.poll() == 0:
                bot.send_message(message.chat.id, package + " sucessfully uninstalled.")
            else:
                bot.send_message(message.chat.id, package + " not uninstalled")
    except Exception as e:
        error = "Error ocurred: " + str(e)
        errorType = "Error type: " + str((e.__class__.__name__))
        bot.send_message(message.chat.id, str(error))
        bot.send_message(message.chat.id, str(errorType))


def encrypt(id):    # cipher users.txt content using SHA256
    m = hashlib.sha256()
    m.update(str(id).encode())
    return m.hexdigest()


def update(message):    # update system
    registerLog(LOG, message)
    try:
        if checkLogin(USERS, message.chat.id):
            action = message.text
            if action == "yes":
                proc = subprocess.Popen('sudo apt-get update -y', shell = True, stdin = None, stdout = subprocess.PIPE, executable = "/bin/bash")
                
                while True:
                    output = proc.stdout.readline()
                    if output == '' and proc.poll() is not None:
                        break
                    if output:
                        bot.send_message(message.chat.id, output.strip())
                proc.wait()
                bot.send_message(message.chat.id, "System updated sucessfully.")
            else:
                 bot.send_message(message.chat.id, "System not updated.")
    except Exception as e:
        error = "Error ocurred: " + str(e)
        errorType = "Error type: " + str((e.__class__.__name__))
        bot.send_message(message.chat.id, str(error))
        bot.send_message(message.chat.id, str(errorType))


def upgrade(message):    # upgrade system
    registerLog(LOG, message)
    try:
        if checkLogin(USERS, message.chat.id):
            action = message.text
            if action == "yes":
                proc = subprocess.Popen('sudo apt-get upgrade -y', shell = True, stdin = None, stdout = subprocess.PIPE, executable = "/bin/bash")
                
                while True:
                    output = proc.stdout.readline()
                    if output == '' and proc.poll() is not None:
                        break
                    if output:
                        bot.send_message(message.chat.id, output.strip())
                proc.wait()
                bot.send_message(message.chat.id, "System upgraded sucessfully.")
            else:
                 bot.send_message(message.chat.id, "System not upgraded.")
    except Exception as e:
        error = "Error ocurred: " + str(e)
        errorType = "Error type: " + str((e.__class__.__name__))
        bot.send_message(message.chat.id, str(error))
        bot.send_message(message.chat.id, str(errorType))


def showforbidden():
    res = ""
    for element in FORBIDDENCOMMANDS:
        res += element + ", "
    return res[:-2]


@bot.message_handler(commands = ['upgrade'])
def upgradeCommand(message):
    registerLog(LOG, message)
    if checkLogin(USERS, message.chat.id) and message.text == "/upgrade":
        bot.send_message(message.chat.id, "Upgrade system? (Write yes/no):")
        bot.register_next_step_handler(message, upgrade)


@bot.message_handler(commands = ['update'])
def updateCommand(message):
    registerLog(LOG, message)
    if checkLogin(USERS, message.chat.id) and message.text == "/update":
        bot.send_message(message.chat.id, "Update system? (Write yes/no):")
        bot.register_next_step_handler(message, update)


@bot.message_handler(commands = ['install'])
def installCommand(message):
    registerLog(LOG, message)
    if checkLogin(USERS, message.chat.id) and message.text == "/install":
        bot.send_message(message.chat.id, "Write package name.")
        bot.register_next_step_handler(message, install)


@bot.message_handler(commands = ['uninstall'])
def uninstallCommand(message):
    registerLog(LOG, message)
    if checkLogin(USERS, message.chat.id) and message.text == "/uninstall":
        bot.send_message(message.chat.id, "Write package name.")
        bot.register_next_step_handler(message, uninstall)


@bot.message_handler(commands = ['forbidden'])
def forbiddenCommand(message):
    bot.send_message(message.chat.id, "Currently forbidden commands: " + str(showforbidden()))


@bot.message_handler(commands = ['help'])
def send_welcome(message):
    registerLog(LOG, message)
    bot.send_message(message.chat.id, "Current version: " + VERSION)
    bot.send_message(message.chat.id, "Welcome to telegramShell, this bot allows you to remotely control a computer terminal.")
    bot.send_message(message.chat.id, "List of avaliable commands: \n- To install packages use /install \n- To update system use /update \n- To upgrade system use /upgrade \n- To view forbidden commands use /forbidden \n- To use the rest of the commands use /run")


@bot.message_handler(commands = ['run'])
@bot.message_handler(func = lambda message: True)
def run(message):
    registerLog(LOG, message)
    if checkLogin(USERS, message.chat.id) and message.text == "/run":
        bot.send_message(message.chat.id, "You can write commands now.")
    elif checkLogin(USERS, message.chat.id):
        command = message.text

        if command[0:2] == "cd":
            try:
                os.chdir(message.text[3:])
                bot.send_message(message.chat.id,"Current directory: " + str(os.getcwd()))
            except Exception as e:
                bot.send_message(message.chat.id, str(e))

        elif command.split()[0] in FORBIDDENCOMMANDS:
            bot.send_message(message.chat.id,"Forbidden command.")

        elif command[0:4] == "sudo" and not ROOT:
            bot.send_message(message.chat.id,"root commands are disabled.")

        elif command[0:4] == "ping" and len(command.split()) == 2:    # infinite ping fix
            ip = str(command).split()[1]
            com = "ping " + str(ip) + " -c 4"
            try:
                p = subprocess.Popen(com, stdout = subprocess.PIPE, shell = True, cwd = os.getcwd(), bufsize = 1)
                for line in iter(p.stdout.readline, b''):
                    try:
                        bot.send_message(message.chat.id, line)
                    except:
                        pass
                p.communicate()
                if p.returncode != 0: 
                    bot.send_message(message.chat.id, " Name or service not known")
            except Exception as e:
                error = "Error ocurred: " + str(e)
                errorType = "Error type: " + str((e.__class__.__name__))
                bot.send_message(message.chat.id, str(error))
                bot.send_message(message.chat.id, str(errorType))

        elif command[0:3] == "top":
            try:
                com = "top -b -n 1 | awk '{print $1, $2, $5, $8, $9, $10, $NF}' > top.txt"
                p = subprocess.Popen(com, stdout = subprocess.PIPE, shell = True, cwd = os.getcwd(), bufsize = 1)
                time.sleep(1)

                com = "cat top.txt"    
                p = subprocess.Popen(com, stdout = subprocess.PIPE, shell = True, cwd = os.getcwd(), bufsize = 1)
                
                for line in iter(p.stdout.readline, b''):
                    try:
                        bot.send_message(message.chat.id, line)
                    except:
                        pass

                time.sleep(1)
                com = "rm top.txt"
                p = subprocess.Popen(com, stdout = subprocess.PIPE, shell = True, cwd = os.getcwd(), bufsize = 1)
            except Exception as e:
                            bot.send_message(message.chat.id, str(e))

        else:
            try:
                p = subprocess.Popen(command, stdout = subprocess.PIPE, shell = True, cwd = os.getcwd(), bufsize = 1)
                for line in iter(p.stdout.readline, b''):
                    if len(str(line)) == 5:    # Empty message that raises api error
                        bot.send_message(message.chat.id, "܁")    # Send special character (U+0701)
                    else:
                        try:
                            bot.send_message(message.chat.id, line)
                        except Exception as e:
                            bot.send_message(message.chat.id, str(e))
                error = p.communicate()
                p.wait()
                if p.returncode != 0: 
                    bot.send_message(message.chat.id, "error " + str(p.stdout.read()))
            except Exception as e:
                #error = "Error ocurred: " + str(e)
                #errorType = "Error type: " + str((e.__class__.__name__))
                error = "Error: Command not found"
                bot.send_message(message.chat.id, str(error))
                #bot.send_message(message.chat.id, str(errorType))


def register(file, user):    # register user and allow him to access the system
    encryptedUser = encrypt(user)
    f = open(file, "a+")
    content = f.readlines()
    content = [x.strip() for x in content]
    if not encryptedUser in content:
        f.write(str(encryptedUser) + "\n")
    f.close


def checkLogin(file, login):    # check if user ID is on users.txt
    encryptedLogin = encrypt(login)
    check = False
    with open(file) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        if encryptedLogin in content:
            check = True
    return check


def registerLog(file, command):    # register user, id, date and command
    f = open(file, "a+")
    now = datetime.datetime.now().strftime("%m-%d-%y %H:%M:%S ")
    f.write(now + "[" + str(command.from_user.username) + " (" + str(command.chat.id) + ")] " + str(command.text) + "\n")
    f.close()



if __name__ == "__main__":

    bot.polling(none_stop = True)
