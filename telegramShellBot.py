import subprocess
import os
import datetime
import hashlib
import time
import re
import telebot
from telebot import types


__author__ = "EnriqueMoran"

__version__ = "v1.3.3"


TOKEN = None
VERSION = None
PASSWORD = None
USERS = None    # users.txt path
LOG = None    # log.txt path
LOGLINES = 0    # Current lines of log.txt
SHAREFOLDER = None    # Shared files storage folder path
LOGLIMIT = None    # Max number of lines to register in log
FORBIDDENCOMMANDS = [
    "wait", "exit", "clear", "aptitude", "raspi-config",
    "nano", "dc", "htop", "ex", "expand", "vim", "man", "apt-get", "poweroff",
    "reboot", "ssh", "scp", "wc"
    ]    # non working commands due to API error or output eror


def load_config(configFile):
    global VERSION, TOKEN, PASSWORD, USERS, LOG, LOGLIMIT, ROOT, \
        SHAREFOLDER, LOGLINES

    file = open(configFile, "r")
    lines = file.read().splitlines()
    cont = 0
    read = False

    for line in lines:
        if cont == 5 and line[:1] != "" and read is True:
            VERSION = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 6 and line[:1] != "" and read is True:
            TOKEN = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 9 and line[:1] != "" and read is True:
            PASSWORD = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 12 and line[:1] != "" and read is True:
            SHAREFOLDER = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 16 and line[:1] != "" and read is True:
            USERS = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 19 and line[:1] != "" and read is True:
            LOG = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 20 and line[:1] != "" and read is True:
            LOGLIMIT = int([file.strip() for file in line.split('=')][1])
            read = False
        if cont == 23 and line[:1] != "" and read is True:
            ROOT = bool([file.strip() for file in line.split('=')][1])
            read = False
        if line[:1] == "#":
            cont += 1
            read = True

config_path = os.getcwd() + "/config.txt"
load_config(config_path)

f1 = open(LOG, "a+")
f1.close
f2 = open(USERS, "a+")
f2.close

with open(LOG) as f:
    LOGLINES = sum(1 for _ in f)

os.makedirs(SHAREFOLDER, exist_ok=True)

bot = telebot.TeleBot(TOKEN)
markup = types.ForceReply(selective=False)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    register_log(LOG, message)
    if not check_config(message):
        if check_login(USERS, message.chat.id):
            bot.send_message(message.chat.id, "Welcome, use /run to start " +
                             "or /help to view info about " +
                             "avaliable commands.")
        else:
            msg = bot.send_message(message.chat.id, "Please log in, insert " +
                                   "password.", reply_markup=markup)
            bot.register_next_step_handler(msg, validate)
    else:
        bot.send_message(message.chat.id, "Please add the necessary data " +
                         "to configuration file and use /start command.")


def check_config(message):
    error = False
    error_msg = "Config file not properly filled, errors:"
    if "./" in SHAREFOLDER:
        error = True
        error_msg += "\n- Share Folder path field is empty."
    if PASSWORD == "":
        error = True
        error_msg += "\n- Password field is empty."
    if USERS == "":
        error = True
        error_msg += "\n- Users File path field is empty."
    if "./" in USERS:
        error = True
        error_msg += "\n- Users File path is relative."
    if LOG == "":
        error = True
        error_msg += "\n- Log File path field is empty."
    if "./" in LOG:
        error = True
        error_msg += "\n- Log File path is relative."
    if LOGLIMIT == "":
        error = True
        error_msg += "\n- Log limit field is empty."
    if ROOT == "":
        error = True
        error_msg += "\n- Root field is empty."
    if error:
        bot.send_message(message.chat.id, error_msg)
    return error


def validate(message):
    register_log(LOG, message)
    if message.text == PASSWORD:
        bot.send_message(message.chat.id, "Logged in, please use /run to " +
                         "start.")
        register(USERS, message.chat.id)
    else:
        msg = bot.send_message(message.chat.id, "Incorrect user/pasword, " +
                               "try again.", reply_markup=markup)
        bot.register_next_step_handler(msg, validate)


def install(message):    # Install a package
    register_log(LOG, message)
    try:
        if check_login(USERS, message.chat.id):
            if message.text != 'cancel':
                package = message.text
                proc = subprocess.Popen('sudo apt-get install -y ' + package,
                                        shell=True, stdin=None,
                                        stdout=subprocess.PIPE,
                                        executable="/bin/bash")
                already_installed = False

                while True:
                    output = proc.stdout.readline()
                    already_installed = already_installed or \
                        "0 newly installed" in str(output)
                    if output == b'' and proc.poll() is not None:
                        break
                    elif output:
                        bot.send_message(message.chat.id, output.strip())
                proc.wait()

                if already_installed:
                    pass    # Dont send any message
                elif proc.poll() == 0:
                    bot.send_message(message.chat.id, package +
                                     " sucessfully installed.")
                elif proc.poll() == 100:
                    bot.send_message(message.chat.id, "Unable to locate " +
                                     "package " + package + ".")
                else:
                    bot.send_message(message.chat.id, package + " not " +
                                     "installed. Error code: " +
                                     str(proc.poll()))
            else:
                bot.send_message(message.chat.id, "action canceled.")
    except Exception as e:
        error = "Error ocurred: " + str(e)
        errorType = "Error type: " + str((e.__class__.__name__))
        bot.send_message(message.chat.id, str(error))
        bot.send_message(message.chat.id, str(errorType))


def uninstall(message):    # Uninstall a package
    register_log(LOG, message)
    try:
        if check_login(USERS, message.chat.id):
            if message.text != 'cancel':
                package = message.text
                proc = subprocess.Popen('sudo apt-get --purge remove -y ' +
                                        package, shell=True, stdin=None,
                                        stdout=subprocess.PIPE,
                                        executable="/bin/bash")
                already_uninstalled = False

                while True:
                    output = proc.stdout.readline()
                    already_uninstalled = already_uninstalled or \
                        "0 to remove" in str(output)
                    if output == b'' and proc.poll() is not None:
                        break
                    if output:
                        bot.send_message(message.chat.id, output.strip())
                proc.wait()

                if already_uninstalled:
                    pass    # dont send any message
                elif proc.poll() == 0:
                    bot.send_message(message.chat.id, package +
                                     " sucessfully uninstalled.")
                else:
                    bot.send_message(message.chat.id, package +
                                     " not uninstalled. Error code: " +
                                     str(proc.poll()))
            else:
                bot.send_message(message.chat.id, "action canceled.")
    except Exception as e:
        error = "Error ocurred: " + str(e)
        errorType = "Error type: " + str((e.__class__.__name__))
        bot.send_message(message.chat.id, str(error))
        bot.send_message(message.chat.id, str(errorType))


def encrypt(id):    # Cipher users.txt content using SHA256
    m = hashlib.sha256()
    m.update(str(id).encode())
    return m.hexdigest()


def update(message):    # Update system
    register_log(LOG, message)
    try:
        if check_login(USERS, message.chat.id):
            action = message.text
            if action == "yes":
                proc = subprocess.Popen('sudo apt-get update -y', shell=True,
                                        stdin=None, stdout=subprocess.PIPE,
                                        executable="/bin/bash")
                while True:
                    output = proc.stdout.readline()
                    if output == b'' and proc.poll() is not None:
                        break
                    if output:
                        bot.send_message(message.chat.id, output.strip())
                proc.wait()

                if proc.poll() == 0:
                    bot.send_message(message.chat.id, "System updated " +
                                     "sucessfully.")
                else:
                    bot.send_message(message.chat.id, "System not updated" +
                                     ", error code: " + str(proc.poll()))
            else:
                bot.send_message(message.chat.id, "System not updated.")
    except Exception as e:
        error = "Error ocurred: " + str(e)
        errorType = "Error type: " + str((e.__class__.__name__))
        bot.send_message(message.chat.id, str(error))
        bot.send_message(message.chat.id, str(errorType))


def upgrade(message):    # Upgrade system
    register_log(LOG, message)
    try:
        if check_login(USERS, message.chat.id):
            action = message.text
            if action == "yes":
                proc = subprocess.Popen('sudo apt-get upgrade -y', shell=True,
                                        stdin=None, stdout=subprocess.PIPE,
                                        executable="/bin/bash")
                while True:
                    output = proc.stdout.readline()
                    if output == b'' and proc.poll() is not None:
                        break
                    if output:
                        bot.send_message(message.chat.id, output.strip())
                proc.wait()

                if proc.poll() == 0:
                    bot.send_message(message.chat.id, "System upgraded " +
                                     "sucessfully.")
                else:
                    bot.send_message(message.chat.id, "System not upgraded" +
                                     ", error code: " + str(proc.poll()))
            else:
                bot.send_message(message.chat.id, "System not upgraded.")
    except Exception as e:
        error = "Error ocurred: " + str(e)
        errorType = "Error type: " + str((e.__class__.__name__))
        bot.send_message(message.chat.id, str(error))
        bot.send_message(message.chat.id, str(errorType))


def show_forbidden():
    res = ""
    for element in FORBIDDENCOMMANDS:
        res += element + ", "
    return res[:-2]


@bot.message_handler(commands=['upgrade'])
def upgradeCommand(message):
    register_log(LOG, message)
    if check_login(USERS, message.chat.id) and message.text == "/upgrade":
        bot.send_message(message.chat.id, "Upgrade system? (Write yes/no):")
        bot.register_next_step_handler(message, upgrade)


@bot.message_handler(commands=['update'])
def updateCommand(message):
    register_log(LOG, message)
    if check_login(USERS, message.chat.id) and message.text == "/update":
        bot.send_message(message.chat.id, "Update system? (Write yes/no):")
        bot.register_next_step_handler(message, update)


@bot.message_handler(commands=['install'])
def installCommand(message):
    register_log(LOG, message)
    if check_login(USERS, message.chat.id) and message.text == "/install":
        bot.send_message(message.chat.id, "Write package name to install or" +
                         " 'cancel' to exit.")
        bot.register_next_step_handler(message, install)


@bot.message_handler(commands=['uninstall'])
def uninstallCommand(message):
    register_log(LOG, message)
    if check_login(USERS, message.chat.id) and message.text == "/uninstall":
        bot.send_message(message.chat.id, "Write package name to uninstall " +
                         "or 'cancel' to exit.")
        bot.register_next_step_handler(message, uninstall)


@bot.message_handler(commands=['forbidden'])
def forbiddenCommand(message):
    bot.send_message(message.chat.id, "Currently forbidden commands: " +
                     str(show_forbidden()))


@bot.message_handler(commands=['help'])
def send_welcome(message):
    register_log(LOG, message)
    bot.send_message(message.chat.id, "Current version: " + VERSION)
    bot.send_message(message.chat.id, "Welcome to telegramShell, this bot " +
                     "allows you to remotely control a computer terminal.")
    bot.send_message(message.chat.id, "List of avaliable commands: \n- To " +
                     "install packages use /install \n- To update system " +
                     "use /update \n-To upgrade system use /upgrade \n- To " +
                     "view forbidden commands use /forbidden \n- To use " +
                     "the rest of the commands use /run")
    bot.send_message(message.chat.id, "You can send files to the computer, " +
                     "also download by using getfile + path (e.g. getfile " +
                     "/home/user/Desktop/file.txt).")


@bot.message_handler(commands=['run'])
@bot.message_handler(func=lambda message: True)
def run(message):
    register_log(LOG, message)
    if check_login(USERS, message.chat.id) and message.text == "/run":
        bot.send_message(message.chat.id, "You can write commands now.")

    elif check_login(USERS, message.chat.id):
        command = message.text
        if command[0:2] == "cd":
            try:
                os.chdir(message.text[3:])
                bot.send_message(message.chat.id, "Current directory: " +
                                 str(os.getcwd()))
            except Exception as e:
                bot.send_message(message.chat.id, str(e))

        elif command.split()[0] in FORBIDDENCOMMANDS:
            bot.send_message(message.chat.id, "Forbidden command.")

        elif command[0:4] == "sudo" and not ROOT:
            bot.send_message(message.chat.id, "root commands are disabled.")

        elif command[0:4] == "ping" and len(command.split()) == 2:
            ip = str(command).split()[1]
            com = "ping " + str(ip) + " -c 4"    # Infinite ping fix
            try:
                p = subprocess.Popen(com, stdout=subprocess.PIPE, shell=True,
                                     cwd=os.getcwd(), bufsize=1)
                for line in iter(p.stdout.readline, b''):
                    try:
                        bot.send_message(message.chat.id, line)
                    except:
                        pass
                p.communicate()
                if p.returncode != 0:
                    bot.send_message(message.chat.id, " Name or service " +
                                     "not known")
            except Exception as e:
                error = "Error ocurred: " + str(e)
                errorType = "Error type: " + str((e.__class__.__name__))
                bot.send_message(message.chat.id, str(error))
                bot.send_message(message.chat.id, str(errorType))

        elif command[0:3] == "top":
            try:
                com = "top -b -n 1 |  \
                awk '{print $1, $2, $5, $8, $9, $10, $NF}' > \
                Qv0g09khgKtop4A80GUjQvU.txt"
                p = subprocess.Popen(com, stdout=subprocess.PIPE, shell=True,
                                     cwd=os.getcwd(), bufsize=1)
                time.sleep(1)

                com = "cat Qv0g09khgKtop4A80GUjQvU.txt"
                p = subprocess.Popen(com, stdout=subprocess.PIPE, shell=True,
                                     cwd=os.getcwd(), bufsize=1)
                doc = open('Qv0g09khgKtop4A80GUjQvU.txt', 'rb')
                bot.send_document(message.chat.id, doc)

                time.sleep(1)
                com = "rm Qv0g09khgKtop4A80GUjQvU.txt"
                p = subprocess.Popen(com, stdout=subprocess.PIPE, shell=True,
                                     cwd=os.getcwd(), bufsize=1)
            except Exception as e:
                            bot.send_message(message.chat.id, str(e))

        elif command[0:7] == "getfile":
            file_path = os.path.join(message.text[7:].strip())
            if os.path.isfile(file_path):
                bot.send_message(message.chat.id, "Sending file.")
                doc = open(file_path, 'rb')
                bot.send_document(message.chat.id, doc)
            else:
                bot.send_message(message.chat.id, "File doesn't exists.")

        else:
            try:
                p = subprocess.Popen(command, stdout=subprocess.PIPE,
                                     shell=True, cwd=os.getcwd(), bufsize=1)
                for line in iter(p.stdout.readline, b''):
                    decoded = line.decode('windows-1252').strip()
                    if len(re.sub('[^A-Za-z0-9]+', '', decoded)) <= 0:
                        # Empty message that raises api 400 error
                        # Send special blank character (U+0701)
                        bot.send_message(message.chat.id, "܁")
                    else:
                        try:
                            bot.send_message(message.chat.id, line)
                        except Exception as e:
                            bot.send_message(message.chat.id, str(e))
                error = p.communicate()
                p.wait()
                if p.returncode != 0:
                    bot.send_message(message.chat.id, "error " +
                                     str(p.stdout.read()))
            except Exception as e:
                error = "Error: Command not found"
                bot.send_message(message.chat.id, str(error))


@bot.message_handler(content_types=['document'])
def saveDoc(doc):
    file_info = bot.get_file(doc.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_path = SHAREFOLDER + doc.document.file_name
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(doc.chat.id, f"File saved as {file_path}")


@bot.message_handler(content_types=['photo'])
def savePhoto(doc):
    bot.send_message(message.chat.id, "To save images send it as file.")


def register(file, user):    # Register user and allow him to access
    encrypted_user = encrypt(user)
    f = open(file, "a+")
    content = f.readlines()
    content = [x.strip() for x in content]
    if encrypted_user not in content:
        f.write(str(encrypted_user) + "\n")
    f.close


def check_login(file, login):    # Check if user ID is on users.txt
    encrypted_login = encrypt(login)
    check = False
    with open(file) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        if encrypted_login in content:
            check = True
    return check


def register_log(file, command):    # Register user, id, date and command
    global LOGLINES, LOGLIMIT
    LOGLINES += 1
    with open(file, 'a+') as f:
        now = datetime.datetime.now().strftime("%m-%d-%y %H:%M:%S ")
        f.write(now + "[" + str(command.from_user.username) + " (" +
                str(command.chat.id) + ")]: " + str(command.text) + "\n")
    if LOGLIMIT > 0 and LOGLINES > LOGLIMIT:
        with open(file) as f:
            lines = f.read().splitlines(True)
        with open(file, 'w+') as f:
            f.writelines(lines[abs(LOGLINES - LOGLIMIT):])


if __name__ == "__main__":
    print("Bot running...")
    bot.polling(none_stop=True)
