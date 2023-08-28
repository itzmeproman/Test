import os
import subprocess
import threading
from telegram import Update, CallbackContext
from telegram.ext import MessageHandler, Filters

# Your bot token
BOT_TOKEN = "6154222206:AAFxkaTRgMI52biIT3m4qAUDwsWIySnoY2c"

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome to the Video Encoder Bot! Send me a video to convert to 480p.")

def process_video(update: Update, context: CallbackContext) -> None:
    def send_progress_message(chat_id, message, total_steps):
        for step in range(total_steps + 1):
            progress = (step / total_steps) * 100
            context.bot.send_message(chat_id=chat_id, text=f"{message} {progress:.2f}%")
            threading.Event().wait(1)  # Wait for 1 second

    video_file = update.message.document.get_file()
    video_path = video_file.download("input.mp4")

    send_progress_message(update.message.chat_id, "Downloading:", 10)  # 10 steps

    output_path = "output.mp4"
    command = [
        "ffmpeg", "-i", video_path, "-vf", "scale=-1:480", output_path
    ]

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    send_progress_message(update.message.chat_id, "Encoding:", 10)  # 10 steps

    with open(output_path, "rb") as f:
        update.message.reply_video(video=f)

    send_progress_message(update.message.chat_id, "Uploading:", 5)  # 5 steps

    # Clean up temporary files
    os.remove(video_path)
    os.remove(output_path)

def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.types.Document.mime_type("video/*"), process_video))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

