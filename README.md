# remoteTelegramShell
remoteTelegramShell is a secure remote shell for Linux that makes use of Telegram's secure conection to send commands and receive messages from the computer. Has an user login system and root restriction in order to avoid malicious connections from other Telegram users.

Also has a log file for tracking users input, that registers the date, command and user ID.

![alt tag](https://i.gyazo.com/5deae4fb4950b30a9549fee0d87dce98.gif)


## How it works
In order to access to computer control, Telegram users must log into the system. IDs of users who write the password correctly will be stored in a text file that grant future accesses. 

Once the user is logged in, commands can be sent. Linux computer receives and executes them from telegram bot, command output will be shown to user on Telegram.

Telegram bot is running on computer's side. Commands are sent from any (authorized) telegram client and received by telegram bot. 
Commands are sent through python to CMD and excecuted. Command's output is captured by python and sent in real time to telegram user.

![alt tag](https://i.imgur.com/hKa0CkX.png)



## Working commands
Currently there are a set of working commands: most of generating output (on version v0.1_3.4.2). Commands that doesnt generate any kind of output will be received and executed  by the computer; commands that requires user input wont work yet, commands that open or execute files either.
If errors occur on the execution of any command, it will be shown to user in real time.


## Versions
Version syntax is the following: 

![alt tag](https://i.gyazo.com/b943366e012976f46e30489896511b87.png)

* **Main version:** Functional version that meets a series of objectives and requirements.
* **User interface:** Current user input interface version.
* **Code:** Code and functionalities implementation.
* **Bug fixes:** Bugs and errors fixes.


## Version history
Check [project releases](https://github.com/EnriqueMoran/remoteTelegramShell/releases) for more info.
- **v0.1_1.1.1:** *11/24/17* Basic user interface, generate output commands cant be sent, command's output can be received, commands that doesnt generate output wont be executed and user will receive *"Command not executed"* message.
- **v0.1_2.3.1:** *11/25/17* Added multiple user interface options, directory change is now possible, fully working log file, several non generating output command bugs has been fixed.
- **v0.1_3.4.2:** *12/07/17* Added install packages, update and upgrade system options; command output is captured and shown to user in real time. Most of linux basic commands are working, but editing file commands.
- **v0.1_5.5.3:** *12/12/17* Root access disabled, some options removed and new ones added. Huge command quantity has been successfully tested.
- **v0.1_6.6.4:** *12/21/17* Config file added, minor bugs fixed.



