import telebot
import subprocess
import threading
import os
import math
import re
from pymongo import MongoClient

# Telegram Bot Token
BOT_TOKEN = '6154222206:AAFxkaTRgMI52biIT3m4qAUDwsWIySnoY2c'

# MongoDB connection
MONGODB_URI = 'mongodb+srv://papapandey:itzmeproman@itzmeproman1.obpzbn7.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(MONGODB_URI)
db = client['video_bot_db']

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Welcome to the Video Encoder Bot! Send me a video to convert it to 480p.")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Received your video. Encoding to 480p...")

    # Store video processing information in MongoDB
    video_data = {
        'chat_id': chat_id,
        'status': 'processing',
        'progress': 0
    }
    video_id = db.video_processing.insert_one(video_data).inserted_id

    # ... (same code as before up to process.wait())

total_seconds = None

def update_progress():
    while True:
        output = process.stderr.readline()
        if process.poll() is not None:
            break
        if "Duration" in output:
            # ... (same parsing code as before)

        if "time=" in output:
            total_seconds = float(re.search(r"\d+", output).group())
            # ... (same parsing code as before)

            # Update progress in MongoDB
            db.video_processing.update_one(
                {'_id': video_id},
                {'$set': {'progress': progress_percent}}
            )
            
            bot.send_message(chat_id, output)

    threading.Thread(target=update_progress).start()

    process.wait()
    bot.send_message(chat_id, "Encoding complete! Sending the encoded video...")
    bot.send_video



    # Update status in MongoDB
    db.video_processing.update_one(
        {'_id': video_id},
        {'$set': {'status': 'completed'}}
    )

    # Clean up files and MongoDB entry
    os.remove(video_path)
    os.remove(output_path)
    db.video_processing.delete_one({'_id': video_id})

if __name__ == "__main__":
    bot.polling(none_stop=True)
            
