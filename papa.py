import telebot
import subprocess
import threading
import os

# Telegram Bot Token
BOT_TOKEN = '6154222206:AAFxkaTRgMI52biIT3m4qAUDwsWIySnoY2c'

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Welcome to the Video Encoder Bot! Send me a video to convert it to 480p.")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Received your video. Encoding to 480p...")

    # Download the video
    video_info = bot.get_file(message.video.file_id)
    video_path = os.path.join('downloads', video_info.file_path)
    video_url = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{video_info.file_path}'
    subprocess.call(['wget', video_url, '-O', video_path])

    # Encode the video
    output_path = os.path.join('outputs', 'output.mp4')
    command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', 'scale=854:480',
        '-c:a', 'aac',
        output_path
    ]

    process = subprocess.Popen(command, stderr=subprocess.PIPE, universal_newlines=True)

    # Create a thread to monitor the process and update progress
    def update_progress():
        while True:
            output = process.stderr.readline()
            if process.poll() is not None:
                break
            bot.send_message(chat_id, output)

    threading.Thread(target=update_progress).start()

    process.wait()
    bot.send_message(chat_id, "Encoding complete! Sending the encoded video...")
    bot.send_video(chat_id, open(output_path, 'rb'))

    # Clean up files
    os.remove(video_path)
    os.remove(output_path)

if __name__ == "__main__":
    bot.polling(none_stop=True)
    
