import datetime
import os
import signal
import re
import subprocess
import telebot
import time

from configparser import ConfigParser
from hashlib import sha256
from json import loads


__author__ = "EnriqueMoran"

__version__ = "v1.4.0"


TOKEN = None
PASSWORD = None               # Used for user authentification
SHARED_FOLDER = None          # Shared files storage folder path
USERS_FILE = None             # users.txt path
LOG_FILE = None               # log.txt path
LOG_LIMIT = None              # Max number of lines to register in log
ENABLE_ROOT = False

LOG_LINES = 0                 # Current lines of log.txt
COMMANDS_QUEUE = {}           # Used for updating and upgrading the system
AUTHENTIFIED_USERS = set()    # Users allowed to send commands
CUSTOM_COMMANDS = []          # Bot custom commands
FORBIDDEN_COMMANDS = []       # Non working/disabled commands
CURRENT_PROCESS = None        # Current process being executed

UPDATE_COMMAND = None         # Command used to update system
UPGRADE_COMMAND = None        # Command used to upgrade system
INSTALL_COMMAND = None        # Command used to install a package
REMOVE_COMMAND = None         # Command used to remove a package

CHAT_ID = None                # Chat id to send messages (for custom commands)

bot = None                    # Telebot object


def load_config(config_file):
    global TOKEN, PASSWORD, SHARED_FOLDER, \
           USERS_FILE, LOG_FILE, LOG_LIMIT, ENABLE_ROOT, FORBIDDEN_COMMANDS, \
           UPDATE_COMMAND, UPGRADE_COMMAND, INSTALL_COMMAND, REMOVE_COMMAND

    config = ConfigParser()
    config.read(config_file)
    TOKEN = config.get('GENERAL', 'token')
    PASSWORD = config.get('GENERAL', 'password')
    SHARED_FOLDER = config.get('FILES', 'shared_folder')
    USERS_FILE = config.get('FILES', 'users_file')
    LOG_FILE = config.get('FILES', 'log_file')
    LOG_LIMIT = int(config.get('FILES', 'log_limit'))
    ENABLE_ROOT = config.getboolean('PERMISSIONS', 'enable_root')
    FORBIDDEN_COMMANDS = loads(config.get('USAGE', 'forbidden_commands'))
    UPDATE_COMMAND = config.get('USAGE', 'update_command')
    UPGRADE_COMMAND = config.get('USAGE', 'upgrade_command')
    INSTALL_COMMAND = config.get('USAGE', 'install_command')
    REMOVE_COMMAND = config.get('USAGE', 'uninstall_command')


def initialize():
    """
    Read config and create configured files and folders.
    """
    global COMMANDS_QUEUE, CUSTOM_COMMANDS

    config_path = os.getcwd() + "/config.txt"
    load_config(config_path)
    error, error_msg = check_config()

    CUSTOM_COMMANDS = ["/update", "/upgrade", "/install",
                       "/remove", "/forbidden", "/help",
                       "/reload", "/stop", "/getfile"]
    COMMANDS_QUEUE = {
                      'update': set(),
                      'upgrade': set(),
                      'install': {},
                      'uninstall': {},
                      'insert_password': set()
    }

    if not error:
        os.makedirs(SHARED_FOLDER, exist_ok=True)
        f1 = open(LOG_FILE, "a+")
        f1.close
        f2 = open(USERS_FILE, "a+")
        f2.close

        with open(LOG_FILE) as f:
            LOG_LINES = sum(1 for _ in f)
    else:
        print(error_msg)
        exit()


def check_config():
    global TOKEN, PASSWORD, SHARED_FOLDER, \
           USERS_FILE, LOG_FILE, LOG_LIMIT, ENABLE_ROOT, FORBIDDEN_COMMANDS, \
           UPDATE_COMMAND, UPGRADE_COMMAND, INSTALL_COMMAND, REMOVE_COMMAND

    error = False
    error_msg = "Config file not properly filled, errors:"
    if not PASSWORD or len(PASSWORD) <= 0:
            error = True
            error_msg += "\n- Password field is empty."
    if not SHARED_FOLDER or len(SHARED_FOLDER) <= 0:
        error = True
        error_msg += "\n- Shared folder field is empty."
    if "./" in SHARED_FOLDER:
        error = True
        error_msg += "\n- Shared folder path is relative."
    if not USERS_FILE or len(USERS_FILE) <= 0:
        error = True
        error_msg += "\n- Users file field is empty."
    if "./" in USERS_FILE:
        error = True
        error_msg += "\n- Users file field is relative."
    if not LOG_FILE or len(LOG_FILE) <= 0:
        error = True
        error_msg += "\n- Log file field is empty."
    if "./" in LOG_FILE:
        error = True
        error_msg += "\n- Log file path is relative."
    if not LOG_LIMIT or LOG_LIMIT < 0:
        error = True
        error_msg += "\n- Log limit wrong value."
    if type(ENABLE_ROOT) is not bool:
        error = True
        error_msg += "\n- Enable root field is empty."
    if not FORBIDDEN_COMMANDS:
        FORBIDDEN_COMMANDS = []
    if not UPDATE_COMMAND:
        error = True
        error_msg += "\n - Update system command is empty."
    if not UPGRADE_COMMAND:
        error = True
        error_msg += "\n - Upgrade system command is empty."
    if not INSTALL_COMMAND:
        error = True
        error_msg += "\n - Install package command is empty."
    if not REMOVE_COMMAND:
        error = True
        error_msg += "\n - Remove package command is empty."
    return error, error_msg


def encrypt(id):
    """
    Cipher user id using SHA256
    """
    m = sha256()
    m.update(str(id).encode())
    return m.hexdigest()


def register_user(user_id):
    """
    Add user to users.txt
    """
    encrypted_user = encrypt(user_id)
    f = open(USERS_FILE, "a+")
    content = [x.strip() for x in f.readlines()]
    if encrypted_user not in content:
        f.write(str(encrypted_user) + "\n")
    f.close()


def check_user(message):
    """
    Check if user ID is registered in users.txt
    """
    global AUTHENTIFIED_USERS

    id = message.from_user.id
    encrypted_id = encrypt(id)
    check = False
    with open(USERS_FILE) as f:
        content = [x.strip() for x in f.readlines()]
        if encrypted_id in content:
            check = True
    return check


def allow_user(user_id):
    """
    Add user to authentified users set
    """
    global AUTHENTIFIED_USERS

    AUTHENTIFIED_USERS.add(user_id)


def register_log(message):
    """
    Register message in log.txt
    """
    global LOG_LIMIT, LOG_FILE, LOG_LINES
    LOG_LINES += 1
    with open(LOG_FILE, 'a+') as f:
        now = datetime.datetime.now().strftime("%m-%d-%y %H:%M:%S ")
        f.write(now + "[" + str(message.chat.username) + " (" +
                str(message.chat.id) + ")]: " + str(message.text) + "\n")

    if LOG_LIMIT > 0 and LOG_LINES > LOG_LIMIT:
        with open(LOG_FILE) as f:
            lines = f.read().splitlines(True)
        with open(LOG_FILE, 'w+') as f:
            f.writelines(lines[abs(LOG_LINES - LOG_LIMIT):])


def update_system(message):
    """
    Run update command depending on SO distro
    """
    global UPDATE_COMMAND

    output_text = " Updating system"
    loading_items = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
    i = 0
    msg_output = bot.send_message(CHAT_ID, output_text)
    try:
        command = f'echo {message.text} | sudo -S {UPDATE_COMMAND} -y'
        proc = subprocess.Popen(command, shell=True, stdin=None,
                                stdout=subprocess.PIPE,
                                executable="/bin/bash")
        while True:
            output = proc.stdout.readline()
            if output == b'' and proc.poll() is not None:
                break
            bot.edit_message_text(loading_items[i % (len(loading_items))] +
                                  output_text, CHAT_ID,
                                  msg_output.message_id)
            i += 1
        proc.wait()
        if proc.poll() == 0:
            output = "System updated sucessfully."
            bot.edit_message_text(output, CHAT_ID,
                                  msg_output.message_id)
        else:
            output = "System not updated, error code: " + str(proc.poll())
            bot.edit_message_text(output, CHAT_ID,
                                  msg_output.message_id)
    except Exception as e:
        error = str(e) + str((e.__class__.__name__))
        bot.send_message(CHAT_ID, error)


def upgrade_system(message):
    """
    Run upgrade command depending on SO distro
    """
    global UPGRADE_COMMAND

    output_text = " Upgrading system"
    loading_items = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
    i = 0
    msg_output = bot.send_message(CHAT_ID, output_text)
    try:
        command = f'echo {message.text} | sudo -S {UPGRADE_COMMAND} -y'
        proc = subprocess.Popen(command, shell=True, stdin=None,
                                stdout=subprocess.PIPE,
                                executable="/bin/bash")
        while True:
            output = proc.stdout.readline()
            if output == b'' and proc.poll() is not None:
                break
            bot.edit_message_text(loading_items[i % (len(loading_items))] +
                                  output_text, CHAT_ID,
                                  msg_output.message_id)
            i += 1
        proc.wait()
        if proc.poll() == 0:
            output = "System upgraded sucessfully."
            bot.edit_message_text(output, CHAT_ID,
                                  msg_output.message_id)
        else:
            output = "System not upgraded, error code: " + str(proc.poll())
            bot.edit_message_text(output, CHAT_ID,
                                  msg_output.message_id)
    except Exception as e:
        error = str(e) + str((e.__class__.__name__))
        bot.send_message(CHAT_ID, error)


def install_package(message):
    """
    Run install package command depending on SO distro
    """
    global INSTALL_COMMAND

    output_text = " Installing package: " + message.text
    loading_items = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
    i = 0
    msg_output = bot.send_message(CHAT_ID, output_text)
    try:
        command = f'echo {message.text} | sudo -S {INSTALL_COMMAND} -y' + \
                  f' {message.text}'
        proc = subprocess.Popen(command, shell=True, stdin=None,
                                stdout=subprocess.PIPE,
                                executable="/bin/bash")
        already_installed = False

        while True:
            output = proc.stdout.readline()
            already_installed = (already_installed or
                                 "0 newly installed" in str(output))
            if output == b'' and proc.poll() is not None:
                break
            bot.edit_message_text(loading_items[i % (len(loading_items))] +
                                  output_text, CHAT_ID,
                                  msg_output.message_id)
            i += 1
        proc.wait()

        if already_installed:
                    return    # Dont send any message
        if proc.poll() == 0:
            response = f"Package {message.text} sucessfully installed."
            bot.edit_message_text(response, CHAT_ID,
                                  msg_output.message_id)
        else:
            response = f"Package {message.text} not installed. " + \
                        "Error code: " + str(proc.poll())
            bot.edit_message_text(response, CHAT_ID,
                                  msg_output.message_id)
    except Exception as e:
        error = str(e) + str((e.__class__.__name__))
        bot.send_message(CHAT_ID, error)


def remove_package(message):
    """
    Run remove package command depending on SO distro
    """
    global REMOVE_COMMAND

    output_text = " Removing package: " + message.text
    loading_items = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
    i = 0
    msg_output = bot.send_message(CHAT_ID, output_text)
    try:
        command = f'echo {message.text} | sudo -S {REMOVE_COMMAND} -y' + \
                  f' {message.text}'
        proc = subprocess.Popen(command, shell=True, stdin=None,
                                stdout=subprocess.PIPE,
                                executable="/bin/bash")
        already_installed = False

        while True:
            output = proc.stdout.readline()
            already_installed = (already_installed or
                                 "0 to remove" in str(output))
            if output == b'' and proc.poll() is not None:
                break
            bot.edit_message_text(loading_items[i % (len(loading_items))] +
                                  output_text, CHAT_ID,
                                  msg_output.message_id)
            i += 1
        proc.wait()

        if already_installed:
                    return    # Dont send any message
        if proc.poll() == 0:
            response = f"Package {message.text} sucessfully removed."
            bot.edit_message_text(response, CHAT_ID,
                                  msg_output.message_id)
        else:
            response = f"Package {message.text} not removed. " + \
                        "Error code: " + str(proc.poll())
            bot.edit_message_text(response, CHAT_ID,
                                  msg_output.message_id)
    except Exception as e:
        error = str(e) + str((e.__class__.__name__))
        bot.send_message(CHAT_ID, error)


def get_forbidden_commands(message):
    res = ""
    for element in FORBIDDEN_COMMANDS:
        res += element + ", "
    return res[:-2]


def stop_proccess(message):    # Send ctrl+c to current process
    global CURRENT_PROCESS

    msg_id = message.chat.id
    if CURRENT_PROCESS:
        CURRENT_PROCESS.send_signal(signal.SIGINT)
        bot.send_message(msg_id, "Ctrl + c sent.")
    else:
        bot.send_message(msg_id, "There is no process running.")


def check_forbidden(message):
    content = message.text.split()
    for elem in content:
        if elem in FORBIDDEN_COMMANDS:
            return True, elem
    return False, None


def send_command(command, message):
    global CURRENT_PROCESS

    """
    Send an empty message to user and edit it with command output
    """
    output = "ㅤ"    # Invisible character
    msg_id = message.chat.id
    msg_output = bot.send_message(msg_id, output)
    output = ""
    n_lines = 0
    try:
        CURRENT_PROCESS = subprocess.Popen(command, shell=True, stdin=None,
                                           stdout=subprocess.PIPE,
                                           executable="/bin/bash")
        for line in iter(CURRENT_PROCESS.stdout.readline, b''):
            decoded = line.decode('windows-1252').strip()
            if n_lines > 40:
                msg_output = bot.send_message(msg_id, decoded)
                n_lines = 0
                output = ""
            if len(re.sub('[^A-Za-z0-9]+', '', decoded)) <= 0:
                # Empty message that raises api 400 error
                # Send special blank character
                output += "ㅤ\n"
                bot.edit_message_text(output, msg_id,
                                      msg_output.message_id)
            else:
                try:
                    output += line.decode('utf-8')
                    bot.edit_message_text(output, msg_id,
                                          msg_output.message_id)
                except Exception as e:
                    msg_error = str(e)
                    msg_output = bot.send_message(msg_id, msg_error)
                    e_code = str(e).split()[str(e).split().index('code:') +
                                            1][:-1]
                    if int(e_code) == 429:  # Too many request
                        break
            n_lines += 1
        error = CURRENT_PROCESS.communicate()
        CURRENT_PROCESS.wait()
    except Exception as e:
        error = str(e) + e.__class__.__name__
        bot.edit_message_text(error, msg_id, msg_output.message_id)
    code = CURRENT_PROCESS.returncode
    CURRENT_PROCESS = None
    if code == 127:    # Command not found
        output = f"/bin/bash: {command}: Command not found"
        bot.edit_message_text(output, msg_id, msg_output.message_id)
    return code, msg_output


def ask_password(message):
    bot.send_message(message.from_user.id, "Enter sudo password.")


def check_password(passwd):
    com = f"sudo -K | echo {passwd} | sudo -S echo 1"
    proc = subprocess.Popen(com, shell=True, stdin=None,
                            stdout=subprocess.PIPE, executable="/bin/bash")
    for line in iter(proc.stdout.readline, b''):
        return True
    else:
        return False


# Initialize bot
initialize()
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome_msg(message):
    """
    Send welcome message
    """
    global __version__, SHARED_FOLDER

    msg_zero = f"---- pyTelegramShellBot version: {__version__} ----"
    msg_one = "\n\nWelcome to pyTelegramShellBot, this bot allows " + \
              "you to remotely control a computer through shell commands."

    msg_two = "\nList of avaliable commands: " + \
              "\n    **· /update**: Update system using configured " + \
              "package system." + \
              "\n    **· /upgrade**: Upgrade system using configured " + \
              "package system." + \
              "\n    **· /install**: Install a package." + \
              "\n    **· /remove**: Remove an installed package." + \
              "\n    **· /forbidden**: Show unavailable commands." + \
              "\n    **· /help**: Show this message." + \
              "\n    **· /reload**: Load the configuration file again." + \
              "\n    **· /stop**: Send CTRL+C signal to running process." + \
              "\n    **· /getfile**: Download the given file (absolute path)."
    msg_three = "\nSent files to the computer will be saved in" + \
                f" configured shared folder: *{SHARED_FOLDER}*"
    msg_four = "\nYou can download files by using getfile + absolute " + \
               "path (*e.g. getfile /home/user/Desktop/file.txt*)."
    welcome_msg = msg_zero + msg_one + msg_two + msg_three + msg_four
    bot.send_message(message.chat.id, welcome_msg, parse_mode="markdown")


@bot.message_handler(commands=['upgrade'])
def upgrade(message):
    global CHAT_ID

    register_log(message)

    if not check_user(message):
        response = "Please log in, insert a valid password."
        bot.send_message(message.from_user.id, response)
        return

    if check_user(message) and message.text.lower() == "/upgrade":
        bot.send_message(message.chat.id, "Upgrade system? (yes/no):")
        COMMANDS_QUEUE['upgrade'].add(message.from_user.id)
        CHAT_ID = message.chat.id


@bot.message_handler(commands=['update'])
def uppdate(message):
    global CHAT_ID

    register_log(message)

    if not check_user(message):
        response = "Please log in, insert a valid password."
        bot.send_message(message.from_user.id, response)
        return

    if check_user(message) and message.text.lower() == "/update":
        bot.send_message(message.chat.id, "Update system? (yes/no):")
        COMMANDS_QUEUE['update'].add(message.from_user.id)
        CHAT_ID = message.chat.id


@bot.message_handler(commands=['install'])
def install(message):
    global CHAT_ID

    register_log(message)

    if not check_user(message):
        response = "Please log in, insert a valid password."
        bot.send_message(message.from_user.id, response)
        return

    if check_user(message) and message.text == "/install":
        bot.send_message(message.chat.id, "Write package name to install or" +
                         " 'cancel' to exit.")
        COMMANDS_QUEUE['install'][message.from_user.id] = None
        CHAT_ID = message.chat.id


@bot.message_handler(commands=['remove'])
def remove(message):
    global CHAT_ID

    register_log(message)

    if not check_user(message):
        response = "Please log in, insert a valid password."
        bot.send_message(message.from_user.id, response)
        return

    if check_user(message) and message.text == "/remove":
        bot.send_message(message.chat.id, "Write package name to remove " +
                         "or 'cancel' to exit.")
        COMMANDS_QUEUE['uninstall'][message.from_user.id] = None
        CHAT_ID = message.chat.id


@bot.message_handler(commands=['forbidden'])
def show_forbidden(message):
    bot.send_message(message.chat.id, "Currently forbidden commands: " +
                     str(get_forbidden_commands(message)) + ".")


@bot.message_handler(commands=['stop'])
def stop(message):
    stop_proccess(message)


@bot.message_handler(commands=['reload'])
def reload(message):
    initialize()
    bot.send_message(message.chat.id, "Configuration reloaded.")


@bot.message_handler(func=lambda message: True)
def on_message(message):
    """
    Send command to computer and return the output
    """
    global USERS_FILELOGIN, VERSION, FORBIDDEN_COMMANDS, ENABLE_ROOT, \
        AUTHENTIFIED_USERS

    register_log(message)
    msg_id = message.chat.id

    # Register access password
    if msg_id not in AUTHENTIFIED_USERS:
        # Password must be sent only by private (not groups)
        if message.text == PASSWORD and message.chat.type == "private":
            register_user(msg_id)    # Register in users.txt
            allow_user(msg_id)       # Grant access to user
            response = "Logged in, you can use commands now."
            bot.send_message(message.from_user.id, response)
            return

        if not check_user(message):
            response = "Please log in, insert a valid password."
            bot.send_message(message.from_user.id, response)
            return

    # Process custom command after being authorized
    msg_user_id = message.from_user.id
    if message.chat.type == "private" and msg_id \
       in COMMANDS_QUEUE['insert_password']:
        allowed = check_password(message.text)
        if allowed:
            if msg_id in COMMANDS_QUEUE['update']:
                COMMANDS_QUEUE['update'].remove(msg_user_id)
                update_system(message)
            elif msg_id in COMMANDS_QUEUE['upgrade']:
                COMMANDS_QUEUE['upgrade'].remove(msg_user_id)
                upgrade_system(message)
            elif msg_id in COMMANDS_QUEUE['install']:
                install_package(COMMANDS_QUEUE['install'][msg_user_id])
                del COMMANDS_QUEUE['install'][msg_user_id]
            elif msg_id in COMMANDS_QUEUE['uninstall']:
                remove_package(COMMANDS_QUEUE['uninstall'][msg_user_id])
                del COMMANDS_QUEUE['uninstall'][msg_user_id]
            return
        else:
            response = "Wrong password."
            COMMANDS_QUEUE['update'].discard(msg_user_id)
            COMMANDS_QUEUE['upgrade'].discard(msg_user_id)
            COMMANDS_QUEUE['install'].pop(msg_user_id, None)
            COMMANDS_QUEUE['uninstall'].pop(msg_user_id, None)
            bot.send_message(msg_user_id, response)
            return

    # Custom message response
    if message.from_user.id in COMMANDS_QUEUE['update']:
        # User must reply whether update system or not
        if message.text.strip().lower() == 'yes':
            ask_password(message)
            COMMANDS_QUEUE['insert_password'].add(message.from_user.id)
        elif message.text.strip().lower() == 'no':
            COMMANDS_QUEUE['update'].remove(message.from_user.id)
            response = "System won't update."
            bot.send_message(msg_id, response)
        else:
            response = "Please reply 'yes' or 'no'."
            bot.send_message(msg_id, response)
        return

    if message.from_user.id in COMMANDS_QUEUE['upgrade']:
        # User must reply whether update system or not
        if message.text.strip().lower() == 'yes':
            ask_password(message)
            COMMANDS_QUEUE['insert_password'].add(message.from_user.id)
        elif message.text.strip().lower() == 'no':
            COMMANDS_QUEUE['upgrade'].remove(message.from_user.id)
            response = "System won't upgrade."
            bot.send_message(msg_id, response)
        else:
            response = "Please reply 'yes' or 'no'."
            bot.send_message(msg_id, response)
        return

    if message.from_user.id in COMMANDS_QUEUE['install']:
        # User must reply which package to install
        if message.text.strip().lower() == 'cancel':
            del COMMANDS_QUEUE['install'][message.from_user.id]
            response = "No package will be installed."
            bot.send_message(msg_id, response)
        else:
            COMMANDS_QUEUE['install'][message.from_user.id] = message
            ask_password(message)
            COMMANDS_QUEUE['insert_password'].add(message.from_user.id)
        return

    if message.from_user.id in COMMANDS_QUEUE['uninstall']:
        # User must reply which package to uninstall
        if message.text.strip().lower() == 'cancel':
            del COMMANDS_QUEUE['uninstall'][message.from_user.id]
            response = "No package will be removed."
            bot.send_message(msg_id, response)
        else:
            COMMANDS_QUEUE['uninstall'][message.from_user.id] = message
            ask_password(message)
            COMMANDS_QUEUE['insert_password'].add(message.from_user.id)
        return

    forbidden, command = check_forbidden(message)

    if forbidden:
        response = f"{command} is a forbidden command."
        bot.send_message(msg_id, response)

    elif message.text[0:2] == 'cd':
        try:
            os.chdir(message.text[3:])
            response = "Changed directory to " + str(os.getcwd())
            bot.send_message(msg_id, response)
        except Exception as e:
            bot.send_message(msg_id, str(e))

    elif "sudo" in message.text and not ENABLE_ROOT:
        bot.send_message(msg_id, "Root commands are disabled.")

    elif message.text[0:4] == "ping" and len(message.text.split()) == 2:
        # Default ping, without arguments
        ip = str(message.text).split()[1]
        com = "ping " + str(ip) + " -c 4"    # Infinite ping fix
        try:
            code, msg = send_command(com, message)
            if code != 0:
                text = " Name or service not known"
                bot.edit_message_text(text, msg_id, msg.message_id)
        except Exception as e:
            error = "Error ocurred: " + str(e)
            error_type = "Error type: " + str((e.__class__.__name__))
            bot.send_message(msg_id, str(error))
            bot.send_message(msg_id, str(error_type))
    elif message.text[0:3] == "top":
        try:
            # TODO: Use top -b plus message
            msg_text = "ㅤ"    # Invisible character
            c = bot.send_message(msg_id, msg_text)

            for i in range(25):    # Show 25 iterations
                com = "top -b -n 1 -o +%CPU | head -n 15 | awk " + \
                      "'{OFS=\"\\t\"}; {print $1, $2, $5, $8, $9, +" \
                      "$10, $NF}'"

                p = subprocess.Popen(com,
                                     stdout=subprocess.PIPE,
                                     shell=True, cwd=os.getcwd())
                try:
                    top_msg = ""
                    for line in iter(p.stdout.readline,
                                     b''):
                        decoded = line.decode('windows-1252').strip()
                        if len(re.sub('[^A-Za-z0-9]+', '',
                               decoded)) <= 0:
                            top_msg += "\n"
                        else:
                            try:
                                top_msg += line.decode('utf-8')
                            except Exception as e:
                                bot.send_message(msg_id, str(e))
                    bot.edit_message_text(top_msg, msg_id,
                                          c.message_id)
                except Exception as e:
                    output = str(e)
                    bot.send_message(msg_id, output)
                    e_code = str(e).split()[str(e).split().index('code:') +
                                            1][:-1]
                    if int(e_code) == 429:  # Too many request
                        return
        except Exception as e:
            output = str(e)
            bot.send_message(msg_id, output)
            e_code = str(e).split()[str(e).split().index('code:') +
                                    1][:-1]
            if int(e_code) == 429:  # Too many request
                return

    elif message.text[0:8] == "/getfile":
        file_path = os.path.join(message.text[8:].strip())
        if os.path.isfile(file_path):
            doc = open(file_path, 'rb')
            bot.send_document(msg_id, doc)
        else:
            bot.send_message(msg_id, "File doesn't exists.")

    else:    # Any other command
        try:
            send_command(message.text, message)
        except Exception as e:
            error = str(e) + e.__class__.__name__
            bot.send_message(msg_id, error)
    return


@bot.message_handler(content_types=['document'])
def saveDoc(doc):
    if not check_user(doc):
        response = "File not saved. Please log in, insert a valid password."
        bot.send_message(doc.from_user.id, response)
        return

    file_info = bot.get_file(doc.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_path = SHARED_FOLDER + doc.document.file_name
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(doc.chat.id, f"File saved as {file_path}")


@bot.message_handler(content_types=['photo'])
def savePhoto(doc):
    if not check_user(doc):
        response = "Photo not saved. Please log in, insert a valid password."
        bot.send_message(doc.from_user.id, response)
        return

    file_info = bot.get_file(doc.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_path = SHARED_FOLDER + str(doc.date) + ".jpg"
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(doc.chat.id, f"File saved as {file_path}")


def main():
    bot.polling(none_stop=True)


if __name__ == "__main__":
    print("Bot running...")
    main()
