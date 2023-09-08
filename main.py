# ---------- INSTALLATION REQUIREMENTS ---------- #
'''
    pip install python-dotenv
    pip install python-telegram-bot
    python -m pip install pymongo==3.8
    pip3 install pymongo[srv]
'''
# ---------- INSTALLATION REQUIREMENTS ---------- #

# ---------- SECURE APIs AND IDs ---------- #
from typing import Final
from dotenv import load_dotenv
import os

load_dotenv()

# Load the hidden environment variables
TOKEN: Final = os.getenv("TOKEN")
BOT_USERNAME: Final = os.getenv("BOT_USERNAME")
URI: Final = os.getenv("URI")
PASSWORD: Final = os.getenv("PASSWORD")

# ---------- SECURE API TOKEN ---------- #

# ---------- IMPORT TELEGRAM API ---------- #

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

import re

from telegram import Bot
from telegram.error import BadRequest

# ---------- IMPORT TELEGRAM API ---------- #

# ---------- DATABASE SETUP ---------- #

from pymongo.mongo_client import MongoClient
import sqlite3

class Database:
    # creates and connects the local database
    def __init__(self, chat_id):
        self.client = MongoClient(URI)
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
        self.db = self.client.get_database('tags_db')
        self.tags = self.db.tags
        self.chat_id = chat_id

        self.userdata = self.db.userdata
        self.allowedchats = self.db.allowedchats

    #modifies the tag usernames or deletes the tag if usernames is null
    def setup_tag(self, tag_name, usernames, chat_name):
        self.tags.delete_one({'chat_id': self.chat_id, 'tag_name': tag_name})
        
        if usernames:
            self.tags.insert_one({
                'chat_id': self.chat_id,
                'tag_name': tag_name,
                'tag_usernames': usernames,
                'chat_username': chat_name
            })

    # returns the usernames connected in a tag
    def get_tag_usernames(self, tag_name):
        temp_tags = self.tags.find_one({'tag_name': tag_name, 'chat_id': self.chat_id})
        tag_usernames = temp_tags.get('tag_usernames')
        return tag_usernames
    
    #TODO: ids should return an array of id
    def get_ids_from_usernames(self, usernames):
        ids = []

        for username in usernames:
            cursor = self.userdata.find({'username': username})

            for doc in cursor:
                ids.append(doc['user_id'])

        return ids

    # returns the database of tags in the chat
    def view_tags(self):
        cursor = self.tags.find({'chat_id': self.chat_id})
        
        # Collect tag names into a list
        tag_names = [doc['tag_name'] for doc in cursor]
        
        return tag_names
    
    def store_userdata(self, user_id, username):
        temp = self.userdata.find_one({'user_id': user_id})

        if temp:
            # Use update_one with the filter and update document
            self.userdata.update_one({'user_id': user_id}, {'$set': {'username': "@"+username}})
        else:
            # Insert a new document
            self.userdata.insert_one({'user_id': user_id, 'username': "@"+username})

    def authenticate(self, chat_name):
        temp = self.allowedchats.find_one({'chat_id': self.chat_id})
        if temp:
            print("You already signed up")
        else:
            self.allowedchats.insert_one({
                'chat_id': self.chat_id,
                'chat_username': chat_name
            })

    def should_disable_bot(self):
        temp = self.allowedchats.find_one({'chat_id': self.chat_id})
        if temp:
            print("I found your chat id")
            return True
        else:
            print("I didnt find your chat id")
            return False

    # closes the connection to the database
    def close_connection(self):
        return "TODO"
         
# ---------- DATABASE SETUP ---------- #

# ---------- BOT CODE ---------- #

# ---------- CODE OF COMMANDS ---------- #

# starts the bot with a welcoming message
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # --- AUTHENTICATOR --- #
    #check whether user is in group chat or private chat
    message_type: str = update.message.chat.type
    if (message_type == 'group' or message_type == 'supergroup'):
        db = Database(update.message.chat_id)
        if db.should_disable_bot() == False:
            await update.message.reply_text("You are not authorized to use this bot.")
            return
    # --- AUTHENTICATOR --- #

    username = update.message.from_user.username
    user_id = update.message.from_user.id

    db = Database(update.message.chat.id)
    db.store_userdata(user_id, username)

    await update.message.reply_text('''\
Welcome!

Please note that you will have to message this bot again using the same /start command should you choose to change your username in the future.

Thank you! 

- Glee
''')

# modifies the tag with usernames
async def setup_tag_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # --- AUTHENTICATOR --- #
    #check whether user is in group chat or private chat
    message_type: str = update.message.chat.type
    if (message_type == 'group' or message_type == 'supergroup' or message_type == 'private'):
        db = Database(update.message.chat_id)
        if db.should_disable_bot() == False:
            await update.message.reply_text("You are not authorized to use this bot.")
            return
    # --- AUTHENTICATOR --- #

    # Get the chat ID and user ID and chat name
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    chat_name = update.message.chat.title

    # Fetch the user's chat member information
    chat_member = await context.bot.get_chat_member(chat_id, user_id)

    # Check if the user is an administrator but disregard if it is not a group chat
    if chat_member.status not in ("administrator", "creator") and update.message.chat.type == 'group':
        await update.message.reply_text("You must be a chat administrator to use this command.")
        return

    text = update.message.text
    processed_text: str = text

    if ('@' in processed_text):
        tags = extract_words_with_at_symbol(text)

    tag_name = tags[0]
    usernames = tags[1:]

    db = Database(update.message.chat.id)
    db.setup_tag(tag_name, usernames, chat_name)
    #db.close_connection()

    await update.message.reply_text("tags updated")

# shows the current tags in the chat
async def view_tags_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # --- AUTHENTICATOR --- #
    #check whether user is in group chat or private chat
    message_type: str = update.message.chat.type
    if (message_type == 'group' or message_type == 'supergroup' or message_type == 'private'):
        db = Database(update.message.chat_id)
        if db.should_disable_bot() == False:
            await update.message.reply_text("You are not authorized to use this bot.")
            return
    # --- AUTHENTICATOR --- #

    db = Database(update.message.chat.id)
    tags = db.view_tags()
    #db.close_connection()

    tags_text = ' '.join(tags)
    await update.message.reply_text(tags_text)

# shows database to users
async def view_database_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Connect to the database
    #chat_id = update.message.chat.id
    client = MongoClient(URI)
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    db = client.get_database('tags_db')
    tags = db.tags

    # Retrieve all documents from the 'tags' collection
    all_documents = list(tags.find())

    print("--- Database ---")
    for document in all_documents:
        print(f"Chat ID: {document['chat_id']}")
        print(f"Tag Name: {document['tag_name']}")
        
        # Print tag usernames from the array
        print("Tag Usernames:")
        for username in document['tag_usernames']:
            print(f"  {username}")
        
        print("-" * 20)  # Separator between documents

    print("---")

    # Close the connection
    #connection.close()

    await update.message.reply_text("""
    Database printed successfully. Note that only devs have access to the console.
    """)

async def authenticate_command(update:Update, context: ContextTypes.DEFAULT_TYPE):
    #show inline query
    #make sure only admin 
    text = update.message.text
    if text == "/authenticate " + PASSWORD:
        db = Database(update.message.chat_id)
        db.authenticate(update.message.chat.title)
        reply = "Password accepted"
    else:
        reply = "Try again"

    await update.message.reply_text(reply)

# show count for tweet posts by paragraph
async def kasyaba_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # --- AUTHENTICATOR --- #
    #check whether user is in group chat or private chat
    message_type: str = update.message.chat.type
    if (message_type == 'group' or message_type == 'supergroup' or message_type == 'private'):
        db = Database(update.message.chat_id)
        if db.should_disable_bot() == False:
            await update.message.reply_text("You are not authorized to use this bot.")
            return
    # --- AUTHENTICATOR --- #

    if (update.message.reply_to_message.text) or (update.message.reply_to_message.caption):
        if update.message.reply_to_message.text:
            text: str = update.message.reply_to_message.text
        else:
            text: str = update.message.reply_to_message.caption
        reply: str = ""

        paragraphs = text.split("\n\n")

        for i in range(0, len(paragraphs), 1):
            reply += get_count(paragraphs[i], i+1) + " \n"
    else:
        reply = "beh i-reply mo sa tweet"
    
    await update.message.reply_text(reply)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # --- AUTHENTICATOR --- #
    #check whether user is in group chat or private chat
    message_type: str = update.message.chat.type
    if (message_type == 'group' or message_type == 'supergroup'):
        db = Database(update.message.chat_id)
        if db.should_disable_bot() == False:
            await update.message.reply_text("You are not authorized to use this bot.")
            return
    # --- AUTHENTICATOR --- #

    text: str = '''\
    To add a new tag, use the /setuptag command.
/setuptag @<name of tag> @<users>

To edit a tag, you will have to repeat the instructions above.

To delete a tag, enter the following: /setuptag @<tag name>

Note that the user must be an admin to be able to use these commands.
    '''
    await update.message.reply_text(text)

# ---------- CODE OF COMMANDS ---------- #

# ---------- MESSAGE HANDLER ---------- #

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # --- AUTHENTICATOR --- #
    #check whether user is in group chat or private chat
    message_type: str = update.message.chat.type
    if (message_type == 'group' or message_type == 'supergroup'):
        db = Database(update.message.chat_id)
        if db.should_disable_bot() == False:
            await update.message.reply_text("You are not authorized to use this bot.")
            return
    # --- AUTHENTICATOR --- #

    if (update.message.text):
        text: str = update.message.text
    else:
        text: str = update.message.caption

    print(f'User ({update.message.chat.id}) in {message_type}: "text"')

    #NOTE: if commented, bot does not have to be mentioned to work in a group
    '''
    if (message_type == 'group'):
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
    '''

    if ("@" in text):

        usernames = []
        ids = []
        tags = extract_words_with_at_symbol(text)

        db = Database(update.message.chat.id)
        for tag in tags:
            usernames.extend(db.get_tag_usernames(tag))
        #db.close_connection()

        ids.extend(db.get_ids_from_usernames(usernames))

        if ids:
            print("")
            # Generate mention tags for each user ID
            mention_tags = [f'<a href="tg://user?id={id}">-</a>' for id in ids]
            mention_message = ''.join(mention_tags)
            tags_string = ' '.join(tags)

            await update.message.reply_text(
                text = f"🔔 Mentioned {tags_string} " + mention_message,
                parse_mode = ParseMode.HTML
            )

        #usernames_processed = ' '.join(usernames)
        #user_ids = get_user_ids(usernames, update.message.chat.id)
        #await update.message.reply_text("test")
        
# ---------- MESSAGE HANDLER ---------- #

# ---------- DEBUGGER ---------- #
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

# ---------- DEBUGGER ---------- #

# ---------- ASSISTING FUNCTIONS IN CODE OF COMMANDS ---------- #

# Function to create the db instance if it doesn't exist
def create_db_instance():
    global db
    if db is None:
        db = Database()

# returns a list of words with an @ symbol
def extract_words_with_at_symbol(text):
    pattern = r'@\w+'
    words = re.findall(pattern, text)

    return words

# returns count of characters for tweet post and detects links
def get_count(text, num) -> str:
    text_len = len(text)

    link_pattern = r'\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b'

    # Replace links with a fixed-length placeholder
    def replace_links(match):
        return "*" * (23)

    text_no_links = re.sub(link_pattern, replace_links, text)

    # Count the remaining characters 
    character_count = len(text_no_links)

    text_len = character_count


    if (text_len <= 280):
        reply: str = "[T" + str(num) + "] " + str(text_len)
    else:
        reply: str = "[T" + str(num) + "] -" + str(text_len - 280)

    return reply

# TODO: Bot object has no attribute get_chat_members
def get_user_ids(usernames, chat_id):
    bot = Bot(token = TOKEN)
    user_ids = []

    for username in usernames:
        try:
            members = bot.get_chat_members(chat_id=chat_id)
            for member in members:
                if member.user.username == username:
                    user_ids.append(member.user.id)
                    break
        except BadRequest as e:
            print(f"Failed to get members: {str(e)}")

    return user_ids

# ---------- ASSISTING FUNCTIONS IN CODE OF COMMANDS ---------- #

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # CREATES THE DATABASE

    # COMMANDS
    app.add_handler(CommandHandler('authenticate', authenticate_command))
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('setuptag', setup_tag_command))
    app.add_handler(CommandHandler('viewtags', view_tags_command))
    app.add_handler(CommandHandler('viewdatabase', view_database_command))
    app.add_handler(CommandHandler('kasyaba', kasyaba_command))
    app.add_handler(CommandHandler('help', help_command))
    
    #Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #Photos
    app.add_handler(MessageHandler(filters.PHOTO, handle_message))

    #Attachments
    app.add_handler(MessageHandler(filters.ATTACHMENT, handle_message))
    
    # ERRORS
    app.add_error_handler(error)

    # POLLS THE BOT
    print("Polling...")
    app.run_polling(poll_interval=3)

# ---------- BOT CODE ---------- #



