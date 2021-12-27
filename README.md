# remoteTelegramShell
remoteTelegramShell is a remote shell for Linux that makes use of Telegram's conection to send commands and receive their output from the computer.
This tool is specially useful if you want to connect to a computer that is behind a private network without opening ports or just want to control your computer through Telegram, without using any ssh client.

Check [remoteDiscordShell](https://github.com/EnriqueMoran/remoteDiscordShell) out for a similar solution working in Discord.


![alt tag](/readme_images/gif1.gif)


## Features
- Control your computer even if its within a private network.
- Send and download any file to/from your computer.
- All Linux distros supported.
- Login system and root restriction to avoid malicious connections from other users.
- Log system to register every sent command.
- Group support.
- Update/upgrade your system remotely.
- Install/remove any package remotely.
- Ban any command you don't want to be sent to the computer.


![alt tag](/readme_images/gif2.gif)


## How it works
To access to the computer control, Telegram users must log into the system, the password will be asked through DM to any unregistered user who sends a command.

Once the user is logged in, all (allowed) commands sent will be processed by the computer and the generated output will be sent back to the user in real time.

There is a configurable list of forbidden commands that shouldn't be used due to unexpected behaviour (e.g. non generating output commands such nano or vim).

There is a set of special commands for specific actions such update or upgrade the system, the list of avaliable special commands is the following:
- **/update:** Update system.
- **/upgrade:** Upgrade system.
- **/install:** Ask for a package and install it.
- **/uninstall:** Ask for a package, then remove and purge it.
- **/help:** Show help message.
- **/reload:** Load config again.
- **/stop:** Send CTRL+C signal to current running process.
- **/forbidden:** Show forbidden command list.
- **/getfile:** Download the specified file (absolute path).


## Installation guide
First step is downloading this project, use this command:
```
git clone https://github.com/EnriqueMoran/remoteTelegramShell.git
```

After cloning the repository in your own computer (it should be Linux OS), the following step is installing pyTelegramBotApi library (notice that this bot is compatible with python 3.7+, so pip3 might be necessary to use):
```
pip install pyTelegramBotApi
```

1. On telegram, create a new bot (talk to *@BotFather*) and save the token. 

![alt tag](/readme_images/image1.png)

2. For using the bot in groups, you must disable privacy (/setprivacy).

![alt tag](/readme_images/image2.png)

3. Edit *config.txt* file and fill the blanks (file paths MUST be absolute). 

![alt tag](/readme_images/image3.png)

Depending on the chosen directory and if sudo parameter is active, it might be necessary to change access permissions of files, this can be done with chmod command.

4. Last step is executing .py script and start using our computer through Telegram.
```
python3 pyTelegramShellBot.py
python3 pyTelegramShellBot.py &              (this will run the script in background)
```


## Sending and receiving files
To send files just drag and drop on the chat, or click on send file button, they will be stored in configured shared folder.

![alt tag](/readme_images/gif3.gif)


To download files from the computer use "/getfile + path" (e.g. /getfile /home/user/Desktop/test-file.txt).

![alt tag](/readme_images/gif4.gif)


## TODO
- Clean code and use decorators for user checking.
- Parallelize loading messages (update, upgrade, install, remove) to avoid max edition limit.
- Add configurable ignore key to avoid processing messages starting with that character.


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
- **v1.4.0:** (12/27/21) Major changes. Code refactorized, group support added, multiple distro support added, improved security.