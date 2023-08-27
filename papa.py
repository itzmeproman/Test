import os
import subprocess
import time
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, filters




# Global variables
thumbnail = None
admins = [123456789]  # Replace with your admin user IDs
processing_file = None
process_info_message = None
encode_resolution = "480p"
video_codec = "libx264"
encoding_speed = "ultrafast"  # FFmpeg preset

# Bot token and updater initialization
TOKEN = "6154222206:AAFxkaTRgMI52biIT3m4qAUDwsWIySnoY2c"
# Your Telegram bot token
bot_token = "6154222206:AAFxkaTRgMI52biIT3m4qAUDwsWIySnoY2c"

# Initialize the Bot instance
bot = Bot(token=bot_token)

updater = Updater(bot=bot, update_queue=queue.Queue())


dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to the Video Encoder Bot!\nOwner name: bankai")

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("List of available commands:\n"
                              "/start - Start the bot\n"
                              "/help - Show this help message\n"
                              "/resolution - Change video resolution\n"
                              "/codec - Change video codec\n"
                              "/restart - Restart the bot (admin only)\n"
                              "/cancel - Cancel ongoing encoding process (admin or user only)")

def resolution(update: Update, context: CallbackContext):
    # Implement resolution change logic
    pass

def codec(update: Update, context: CallbackContext):
    # Implement codec change logic
    pass

def restart(update: Update, context: CallbackContext):
    # Implement restart logic (admin only)
    pass

def cancel(update: Update, context: CallbackContext):
    # Implement cancel logic (admin or user only)
    pass

def process_video(update: Update, context: CallbackContext):
    global processing_file, process_info_message
    video_file = update.message.video.file_id
    download_start_time = datetime.now()
    
    update.message.reply_text("Downloading video...")
    downloaded_file = context.bot.get_file(video_file)
    downloaded_file.download('input.mp4')
    download_end_time = datetime.now()
    download_duration = download_end_time - download_start_time
    
    update.message.reply_text("Download complete.\nEncoding video to {}...".format(encode_resolution))
    encode_start_time = datetime.now()
    
    # FFmpeg command to encode the video
    ffmpeg_command = [
        "ffmpeg", "-i", "input.mp4", "-c:v", video_codec, "-preset", encoding_speed,
        "-vf", "scale=-1:480", "-c:a", "copy", "output.mp4"
    ]
    subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    encode_end_time = datetime.now()
    encode_duration = encode_end_time - encode_start_time
    
    update.message.reply_text("Encoding complete.\nUploading encoded video...")
    upload_start_time = datetime.now()
    
    context.bot.send_video(chat_id=update.effective_chat.id, video=open('output.mp4', 'rb'))
    upload_end_time = datetime.now()
    upload_duration = upload_end_time - upload_start_time
    
    update.message.reply_text("Upload complete.")
    
    # Display process times
    process_info = (
        f"Process timings:\n"
        f"Download: {download_duration.seconds}.{download_duration.microseconds}s\n"
        f"Encoding: {encode_duration.seconds}.{encode_duration.microseconds}s\n"
        f"Upload: {upload_duration.seconds}.{upload_duration.microseconds}s"
    )
    update.message.reply_text(process_info)

    # Clean up temporary files
    os.remove('input.mp4')
    os.remove('output.mp4')

def process_image(update: Update, context: CallbackContext):
    global thumbnail
    # Process incoming image and set as thumbnail
    pass

def main():
    # Add handlers for different commands and messages
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help_command)
    resolution_handler = CommandHandler('resolution', resolution)
    codec_handler = CommandHandler('codec', codec)
    restart_handler = CommandHandler('restart', restart)
    cancel_handler = CommandHandler('cancel', cancel)
    process_video_handler = MessageHandler(Filters.video, process_video)
    process_image_handler = MessageHandler(Filters.photo, process_image)



    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(resolution_handler)
    dispatcher.add_handler(codec_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(cancel_handler)
    dispatcher.add_handler(process_video_handler)
    dispatcher.add_handler(process_image_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
  
