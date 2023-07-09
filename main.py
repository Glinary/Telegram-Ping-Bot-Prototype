# ---------- INSTALLATION REQUIREMENTS ---------- #
'''
    pip install python-dotenv
    pip install python-telegram-bot
'''
# ---------- INSTALLATION REQUIREMENTS ---------- #

# ---------- SECURE APIs AND IDs ---------- #
from typing import Final
from dotenv import load_dotenv
import os

load_dotenv()

# Load the hidden environment variables
TOKEN: Final = os.getenv("BOT_TOKEN")
BOT_USERNAME: Final = os.getenv("BOT_USERNAME")
SHEET_ID: Final = os.getenv("SHEET_ID")

# ---------- SECURE API TOKEN ---------- #

# ---------- IMPORT TELEGRAM API ---------- #

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

import re

from telegram import Bot

# ---------- IMPORT TELEGRAM API ---------- #

# ---------- DATABASE SETUP ---------- #

import sqlite3

class Database:
    
    # creates and connects the local database
    def __init__(self):
        self.connection = sqlite3.connect('username_data.db')
        self.cursor = self.connection.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS tag (
            tag_name TEXT,
            username TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ids (
            user_id TEXT PRIMARY KEY,
            username TEXT
        )
        """)
        self.connection.commit()

    # store user id
    def store_user_id(self, user_id, username):
        self.cursor.execute("""
        DELETE FROM ids
        WHERE username = '{}'
        """.format(username))
        self.connection.commit()

        self.cursor.execute("""
        INSERT INTO ids VALUES
        ('{}', '{}')
        """.format(user_id, '@' + username))
        self.connection.commit()

    # get user id given username
    def get_user_id(self, username):
        self.cursor.execute("""
        SELECT user_id
        FROM ids
        WHERE username = '{}'
        """.format(username))
        temp = self.cursor.fetchone()
        return temp

    # modifies the tags with usernames
    def setup_tag(self, tag_name, usernames):
        self.cursor.execute("""
        DELETE FROM tag
        WHERE tag_name = '{}'
        """.format(tag_name))
        self.connection.commit()

        for username in usernames:
            self.cursor.execute("""
            INSERT OR IGNORE INTO tag VALUES
            ('{}', '{}')
            """.format(tag_name, username))
        self.connection.commit()

    # returns the usernames connected in a tag
    def get_tag_usernames(self, tag_name):
        self.cursor.execute("""
        SELECT username 
        FROM tag
        WHERE tag_name = '{}'
        """.format(tag_name))
        tag_usernames = [row[0] for row in self.cursor.fetchall()]
        return tag_usernames

    # returns the database of tags in the chat
    def view_tags(self):
        self.cursor.execute("""
        SELECT DISTINCT tag_name
        FROM tag
        """)
        tags = [row[0] for row in self.cursor.fetchall()]
        return tags

    # closes the connection to the database
    def close_connection(self):
        self.connection.close()
         
# ---------- DATABASE SETUP ---------- #

# ---------- BOT CODE ---------- #

# ---------- CODE OF COMMANDS ---------- #

# starts the bot with a welcoming message
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    user_id = user.id
    username = user.username

    # Store the user ID and username in the database
    db.store_user_id(user_id, username)

    await update.message.reply_text(f"Welcome, {user.username}! Glee says hi")

# modifies the tag with usernames
async def setup_tag_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    processed_text: str = update.message.text

    if ('@' in processed_text):
        tags = extract_words_with_at_symbol(text)

    tag_name = tags[0]
    usernames = tags[1:]

    db.setup_tag(tag_name, usernames)
    db.close_connection

    await update.message.reply_text("tags updated")

# shows the current tags in the chat
async def view_tags_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    tags = db.view_tags()
    db.close_connection

    tags_text = ' '.join(tags)
    await update.message.reply_text(tags_text)

# shows database to users
async def view_database_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Connect to the database
    connection = sqlite3.connect('username_data.db')
    cursor = connection.cursor()

    # Fetch the table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Iterate over the tables
    for table in tables:
        table_name = table[0]
        print(f"Table: {table_name}")

        # Fetch the rows from the table
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Print the rows
        for row in rows:
            print(row)

        print()  # Add an empty line between tables

    # Close the connection
    connection.close()

    await update.message.reply_text("""
    Database printed successfully. Note that only devs have access to the console.
    """)

async def mention_ids_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    processed_text: str = update.message.text
    usernames = []
    user_ids = []

    if ('@' in processed_text):
        tags = extract_words_with_at_symbol(text)

    for tag in tags:
        tag_usernames = db.get_tag_usernames(tag)
        usernames.extend(tag_usernames)
    db.close_connection

    for username in usernames:
        user_ids.extend(db.get_user_id(username))

    # Generate mention tags for each user ID
    mention_tags = [f'<a href="tg://user?id={user_id}">.</a>' for user_id in user_ids]
    mention_message = ''.join(mention_tags)
    await update.effective_chat.send_message(
        text = mention_message,
        parse_mode = ParseMode.HTML
    )

#TODO: store in tag table user ids instead

#TODO: make handle message detect any incoming @ instead of mention_ids_command

# ---------- CODE OF COMMANDS ---------- #

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

def extract_words_with_at_symbol(text):
    pattern = r'@\w+'
    words = re.findall(pattern, text)

    return words

async def get_chat_id(chat_username):
    try:
        # Use the get_chat method to retrieve information about the chat
        chat = await bot.get_chat(chat_id=chat_username)
        
        # Extract the chat ID from the retrieved chat information
        chat_id = chat.id
        return chat_id
    except Exception as e:
        print(f"Error retrieving chat ID for chat '{chat_username}': {e}")
        return None


# ---------- ASSISTING FUNCTIONS IN CODE OF COMMANDS ---------- #

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # CREATES THE DATABASE
    db = None
    create_db_instance()

    # COMMANDS
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('setuptag', setup_tag_command))
    app.add_handler(CommandHandler('viewtags', view_tags_command))
    app.add_handler(CommandHandler('viewdatabase', view_database_command))
    app.add_handler(CommandHandler('mentionids', mention_ids_command))

    # ERRORS
    app.add_error_handler(error)

    # POLLS THE BOT
    print("Polling...")
    app.run_polling(poll_interval=3)

# ---------- BOT CODE ---------- #



