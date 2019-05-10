# banlabyrinth
This discord bot supplies your server with new temporary ban strategy. Annoying people could be trapped inside the 
labyrinth or box. A labyrinth visually is a voice channel category with 5 channels in it. After going through the maze 
the user will be restored to their rights.  
Direct link to invite bot: https://discordapp.com/api/oauth2/authorize?client_id=568422729166880778&permissions=286264336&scope=bot
##### Instead of boring temporary ban, you can lock up that bad guy >:) 
![](https://i.imgur.com/1adSSjG.gif)
# Commands
All commands require "Labyrinth Keeper" role to be executed. If that role not created, execute any command once.
* `#trap [member] [size]` - Creates a labyrinth for the member and locks him in it. Size format: NxM , where 
1 < n < 100, 1 < m < 100.  
  Examples: #trap "Bad guy" 20x15 , #trap BadGuy
* `#pardon [member]` Removes the labyrinth and restores member permissions.
* `#box [member]` Creates a box for the member and locks him in it.
* `#unbox [member]` Removes the box and restores member permissions.
* `#help [command]` Info about the command or just a list of commands, if `[commands]` is not provided.
# Installation
1) Check if Python installed on your machine. Otherwise, visit https://www.python.org/
    ```
    # Windows
    $ python
    >>> exit()
    
    # MacOS, Linux
    $ python3
    >>> exit()
    ```
2) Install "virtualenv" package. It will help later with creating a dedicated environment for banlabyrinth.
    ```
    # Windows
    $ pip install virtualenv
    
    # MacOS, Linux
    $ pip3 install virtualenv
    ```
3) Create some folder for the virtual environment and then move in the folder:
    ```
    # Windows
    $ cd /D "YOUR PATH"
    
    # MacOS, Linux
    $ cd YOUR PATH
    ```
4) Create new virtual enviroment and activate it:
    ```
    # Windows
    $ virtualenv venv
    $ venv\Scripts\activate.bat
    
    # MacOS
    $ virtualenv venv
    $ source venv/bin/activate
    
    # Linux
    $ python3 -m virtualenv venv
    $ source venv/bin/activate
    ```
5) Install banlabyrinth
    ```
    # Windows
    $ pip install git+https://github.com/6rayWa1cher/banlabyrinth#egg=banlabyrinth
    
    # MacOS, Linux
    $ pip3 install git+https://github.com/6rayWa1cher/banlabyrinth#egg=banlabyrinth
    ```
6) Run it once, it will create a config.ini file
    ```
    # Windows
    $ python -m banlabyrinth
    
    # MacOS, Linux
    $ python3 -m banlabyrinth
    ```
    It will fail with `ValueError: Discord token not provided in "PATH TO config.ini" !`
7) Go to https://discordapp.com/developers/applications/ and register new bot. 
    Then, copy bot token to `token` (replace `fill_me`) in `config.ini` (see previous step).
8) You're ready to finally run the bot! Execute this each time you wanted to start the bot:
    ```
    # Windows
    $ cd /D "YOUR PATH"
    $ venv\Scripts\python.exe -m banlabyrinth
    
    # MacOS, Linux
    $ cd YOUR PATH
    $ venv/bin/python3 -m banlabyrinth
    ```
9) To stop bot, use Ctrl+Break on Windows or Ctrl+C on MacOS/Linux
# Contributing
You're always welcome with ideas, issues, and other help! 
