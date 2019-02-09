# remoteTelegramShell
remoteTelegramShell is a secure remote shell for Linux that makes use of Telegram's secure conection to send commands and receive messages from the computer. Has an user login system and root restriction in order to avoid malicious connections from other Telegram users. _"pyTelegramBotApi"_ and _"telebot"_ modules are needed. This tool is specially useful for those computers that have ssh port closed.

Also has a log file for tracking users input, that registers the date, command and user ID.

![alt tag](https://i.gyazo.com/5deae4fb4950b30a9549fee0d87dce98.gif)


## How it works
In order to access to computer control, Telegram users must log into the system. IDs of users who write the password correctly will be stored in a text file that grant future accesses. 

Once the user is logged in, commands can be sent. Linux computer receives and executes them from telegram bot, command output will be shown to user on Telegram.

Telegram bot is running on computer's side. Commands are sent from any (authorized) telegram client and received by telegram bot. 
Commands are sent through python to CMD and excecuted. Command's output is captured by python and sent in real time to telegram user.

![alt tag](https://i.imgur.com/hKa0CkX.png)



## Working commands
Currently there are a set of working commands: most of generating output (on version v0.2_6.7.5). Commands that doesnt generate any kind of output will be received and executed  by the computer; commands that requires user input wont work yet, commands that open or execute files either.
If errors occur during the execution of any command, it will be shown to user in real time.



## Instruction guide

First step is downloading this project, this command can be used for it:
```
git clone https://github.com/EnriqueMoran/remoteTelegramShell.git
```

After cloning the repository in your own computer (it must be Linux OS), the following step is installing TelegramBotApi library (using command line):
```
pip install pyTelegramBotApi
```
On telegram we create a new bot (talk to *@BotFather*) and save its token.

![alt tag](https://i.gyazo.com/783e4a87c8bc7dc75cff9a5c2343a8a2.png)

Afterwards we edit the "config.txt" file and fill the blanks. The file paths must be absolute, if you use relative paths you have to stay
in the same directory during the execution (you can't use "cd" to move to others directories). 

![alt tag](https://i.gyazo.com/b2a8e9b5694498813d4261df77e21db8.png)

Depending on the chosen directory it might be necessary to change access permissions of the files, this can be done with the following commands:
```
chmod +777 config.txt

chmod +777 users.txt

chmod +777 telegramShellBot.py

chmod +777 log.txt
```
Last step is executing .py script and start using our computer through Telegram.

![alt tag](https://i.gyazo.com/90245f73d0ffbb6b4d187bdd0637eebe.png)



## Version history
Check [project releases](https://github.com/EnriqueMoran/remoteTelegramShell/releases) for more info.
- **v0.1_1.1.1:** *11/24/17* Basic user interface, generate output commands cant be sent, command's output can be received, commands that doesnt generate output wont be executed and user will receive *"Command not executed"* message.
- **v0.1_2.3.1:** *11/25/17* Added multiple user interface options, directory change is now possible, fully working log file, several non generating output command bugs has been fixed.
- **v0.1_3.4.2:** *12/07/17* Added install packages, update and upgrade system options; command output is captured and shown to user in real time. Most of linux basic commands are working, but editing file commands.
- **v0.1_5.5.3:** *12/12/17* Root access disabled, some options removed and new ones added. Huge command quantity has been successfully tested.
- **v0.2_6.6.4:** *12/21/17* Config file added, minor bugs fixed, user's ID are ciphered on users file.
- **v0.2_6.7.5:** *12/22/17* Last pre-release before v1.0. Forbidden commands are now working properly, several bugs fixed. 


