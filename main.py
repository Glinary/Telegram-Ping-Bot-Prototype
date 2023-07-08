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
BOT_TOKEN: Final = os.getenv("BOT_TOKEN")
BOT_USERNAME: Final = os.getenv("BOT_USERNAME")
SHEET_ID: Final = os.getenv("SHEET_ID")

# ---------- SECURE API TOKEN ---------- #

# ---------- IMPORT TELEGRAM API ---------- #

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.contants import ParseMode

# ---------- IMPORT TELEGRAM API ---------- #

# ---------- BOT CODE ---------- #
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Glee says hi")

async def setuptag_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text: str = update.message.text
    processed_text: str = text.lower()

    if ('@' in processed_text):
        tags = extract_words_with_at_symbol(text)
        
    processed_tags = tags.split(" ")
    tag_name = processed_tags[0]
    usernames = processed_tags[1:]

    #TODO: modify sql here

    await update.message.reply_text("tags updated")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

def extract_words_with_at_symbol(text):
    pattern = r'(?<=@)\w+'
    words = re.findall(pattern, text)

    return words

#TODO: modify function to get user ids given mentioned usernames
def get_user_ids(usernames):
    user_ids = []

    return user_ids

def mention_users(update: Update, context: ContextTypes.DEFAULT_TYPE, user_ids):
    mention_content = [f'<a href="tg://user?id={user_id}">.</a>' for user_id in user_ids]

    mention_message = ''.join(mention_tags)
    update.effective_chat.send_message(
        text = mention_message,
        parse_mode = ParseMode.HTML
    )


if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('setuptag', setuptag_command))

    app.add_error_handler(error)

    print("Polling...")
    app.run_polling(poll_interval=3)

# ---------- BOT CODE ---------- #
# ---------- DATABASE SETUP ---------- #

import sqlite3

class Database:
    
    def __init__(self, tag_name, usernames):
        self.tag_name = tag_name
        self.usernames = usernames


connection = sqlite3.connect('username_data.db')
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tag (
    tag_name TEXT,
    username TEXT
)
""")

cursor.execute("""
INSERT INTO tag VALUES
('@merrs', '@dichiloi'),
('@merrs', '@notraysdump'),
('@merrs', '@jomaguerra')
""")

cursor.execute("""
SELECT username FROM tag t
WHERE tag_name = '@merrs'
""")

usernames = cursor.fetchall()
print(usernames)

connection.commit()
connection.close()

# ---------- DATABASE ---------- #




