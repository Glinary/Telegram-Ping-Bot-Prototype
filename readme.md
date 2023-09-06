# NOTICE

This is a telegram bot that was developed to aid in drafting newsbites for
The LaSallian. While the actual deployed bot is stored in the
[organization's repository](https://github.com/thelasallian/PingBot-OpenSource), this version is the prototype of any
future updates that will be implemented in the bot. 

# Installation

1. Connect using SSH to the VM `ssh -i \path\to\private_key host_name@public_ip`
1. Install the following dependencies. Note that PyMongo 3.6 uses an unstable API and must be updated should there be an issue.
``` 
    sudo apt-get install python3-pip
    sudo apt-get install tmux
    pip install python-telegram-bot
    python -m pip install pymongo==3.6
    pip3 install pymongo[srv]
```
3. In case a PATH warning was displayed, you may add to path
`PATH=$PATH:/location/to/installation/folder`
4. Check if it was successfully added `echo $PATH`
5. Make a shared directory in the root folder `sudo chmod 777 pingloi`
6. Import the python code and move it to the shared directory 
   `sudo mv main.py /pingloi`
7. Check if there are tmux sessions under `/pingloi` directory
8. Enter the shared tmux session `tmux -S /pingloi/shared-session attach-session` if it exists
9. If there are no tmux sessions currently running,
    create a shared tmux session named shared-session using `tmux -S /pingloi/shared-session new-session`
10. If you did not attach to the session automatically, follow instruction 9
11. Run the main code `python3 main.py >> stdout.txt`
12. Detach from the tmux session `ctrl + b` then press `d`
13. Make the new folder accessible to all users `sudo chmod 777 /pingloi/shared-session`
14. Exit the SSH terminal

# How to stop/reset the bot:

1. Access the SSH terminal and navigate to the shared directory
2. You may check the running tmux sessions (optional) under `/pingloi` directory
3. Attach to the shared tmux session.  `tmux -S /pingloi/shared-session attach-session`
4. Stop the code by pressing `ctrl + c` or `cmd + c`
5. Run the code again by typing `python3 main.py >> stdout.txt`
6. Detach from the tmux session `ctrl + b` then press `d`

# Questions/Concerns?

Reach out to the web section or contact the developer through her telegram `@gleezelluy`

# Technologies used
![Python](https://img.shields.io/badge/Python-3776AB.svg?style=for-the-badge&logo=Python&logoColor=white)
![Microsoft Azure](https://img.shields.io/badge/Microsoft%20Azure-0078D4.svg?style=for-the-badge&logo=Microsoft-Azure&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624.svg?style=for-the-badge&logo=Linux&logoColor=black)
![Tmux](https://img.shields.io/badge/tmux-1BB91F.svg?style=for-the-badge&logo=tmux&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248.svg?style=for-the-badge&logo=MongoDB&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-26A5E4.svg?style=for-the-badge&logo=Telegram&logoColor=white)
![PythonAnywhere](https://img.shields.io/badge/PythonAnywhere-1D9FD7.svg?style=for-the-badge&logo=PythonAnywhere&logoColor=white)
