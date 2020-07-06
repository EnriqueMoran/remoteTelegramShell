# remoteTelegramShell
remoteTelegramShell is a secure remote shell for Linux that makes use of Telegram's conection to send commands and receive messages from the computer. It has an user login system and root restriction in order to avoid malicious connections from other Telegram users. _"pyTelegramBotApi"_ module is needed. This tool is specially useful if you want to connect to a computer that is behind a private network without opening ports or just want to control your computer through Telegram, without using any other ssh client.

It also has a log file for tracking users input, that registers the date, command and user ID.

![alt tag](/readme_images/gif1.gif)


## How it works
To access to computer control, Telegram users must log into the system. IDs of users who write the password correctly will be stored in a protected text file that allows future access. 

Once the user is logged in, commands can be sent. Linux computer receives and executes them from telegram bot, commands output will be shown to user on Telegram in real time.

Telegram bot is running on computer's side. Commands are sent from any (authorized) Telegram client and received by Telegram bot. 
Commands are sent through python to CMD and excecuted, the output is captured and sent in real time to the user.

![alt tag](/readme_images/image1.png)



## Working commands
Most of Linux commands can be executed. Those that dont generate any kind of output will be received and executed  by the computer; commands that requires user input wont work yet, commands like nano, htop, vim... arent working neither.
If errors occur during the execution of any command, it will be reported to the user.



## Supported distros
Debian and Ubuntu based distros can be updated and upgraded, install and uninstall packages aswell. 
I am currently working on adding support for the rest of package managers.



## Installation guide
First step is downloading this project, use this command:
```
git clone https://github.com/EnriqueMoran/remoteTelegramShell.git
```

After cloning the repository in your own computer (it must be Linux OS), the following step is installing TelegramBotApi library (using command line):
```
pip install pyTelegramBotApi
```
On telegram, create a new bot (talk to *@BotFather*) and save the token.

![alt tag](/readme_images/image2.png)

Afterwards edit "config.txt" file and fill the blanks. The files paths MUST be absolute, if you use relative paths you have to stay
in the same directory during the execution (you can't use "cd" to move to others directories) and wont be able to run the script on boot (using crontab). 

![alt tag](/readme_images/image3.png)

Depending on the chosen directory and if sudo parameter is active, it might be necessary to change access permissions of the files, this can be done with chmod command.

Last step is executing .py script and start using our computer through Telegram.
```
python3 telegramShellBot.py
python3 telegramShellBot.py &              (this will run the script in background)
```

![alt tag](/readme_images/image4.png)


## Sending and receiving files
To send files just drag and drop on the chat, or click on send file button (images must be sent this way).
To download files from the computer use "getfile + path" (e.g. getfile /home/user/Desktop/test-file.txt).
**Important:** File sending can be done by any user, even if he hasn't logged in, this is currently being fixed.

![alt tag](/readme_images/gif2.gif)


## Roadmap
Future changes and features:
* Improve compatibility with Linux distros (currently, install/uninstall commands uses apt-get).
* Test and improve root option.
* Improve security.
* Fix no user checking file sending (critical).
* Improve Windows compatibility.
* Add parameter to allow file sending.
* Add ctrl+c command.


## Version history
Check [project releases](https://github.com/EnriqueMoran/remoteTelegramShell/releases) for more info.
- **v0.1_1.1.1:** (11/24/17) Basic user interface, generate output commands cant be sent, command's output can be received, commands that doesnt generate output wont be executed and user will receive *"Command not executed"* message.
- **v0.1_2.3.1:** (11/25/17) Added multiple user interface options, directory change is now possible, fully working log file, several non generating output command bugs has been fixed.
- **v0.1_3.4.2:** (12/07/17) Added install packages, update and upgrade system options; command output is captured and shown to user in real time. Most of linux basic commands are working, but editing file commands.
- **v0.1_5.5.3:** (12/12/17) Root access disabled, some options removed and new ones added. Huge command quantity has been successfully tested.
- **v0.2_6.6.4:** (12/21/17) Config file added, minor bugs fixed, user's ID are ciphered on users file.
- **v0.2_6.7.5:** (12/22/17) Last pre-release before v1.0. Forbidden commands are now working properly, several bugs fixed. 
- **v1.0:** (6/21/18) Official release. Critical and minor bug fixed. New forbidden commands added.
- **v1.1.2:** (3/8/19) Typo correction, top command added, Telegram API 400 Bad Request error fixed.
- **v1.2.0:** (1/25/20) Install and uninstall package infinite loop fixed, config.txt and readme modified.
- **v1.2.1:** (1/26/20) Update and upgrade system infinite loop fixed, config parameters checker added.
- **v1.3.1:** (6/12/20) File sending and receiving feature added.
- **v1.3.2:** (6/27/20) Log limit fixed, several non generating output messages fixed, shareFolder parameter edited in config file.
- **v1.3.3:** (6/27/20) PEP8 formatted code, top command changed to send a txt file instead of printing the whole message.


