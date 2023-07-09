This is a telegram bot that was developed to aid the newsbites of
The LaSallian. While the actual deployed bot is stored in the
organization's repository, this version is the prototype of any
future updates being implemented in the bot. 

It uses python and sql to manage the database of user ids
and usernames through chat commands. It can also detect the 
character count of entered paragraphs to simulate a newsbite
being posted on twitter, such as accounting for links.

----------

NOTICE:

The bot currently relies on pythonanywhere.com using a free account, 
so it may slow down once maximum CPU usage has been reached. 
This resets every 22 hours. The bot also relies on Google Sheets 
to add/edit the tags, but an update so that they may be edited using 
only Telegram is currently in progress. 

----------

How to deploy the bot:

1. Use a python hosting service (pythonanywhere.com)
2. Install the following using the bash console:
    "pip install python-telegram-bot"
    "pip install python-dotenv"
3. Save and Run the code
