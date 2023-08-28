import telebot
import subprocess
import threading
import os
import math

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
        # Parse the output to find the time duration (you can adjust the pattern as needed)
        if "Duration" in output:
            duration_match = re.search(r"Duration: (\d+:\d+:\d+.\d+)", output)
            if duration_match:
                duration = duration_match.group(1)
                duration_parts = duration.split(":")
                total_seconds = int(duration_parts[0]) * 3600 + int(duration_parts[1]) * 60 + float(duration_parts[2])
        # Parse the output to find the time progress (you can adjust the pattern as needed)
        if "time=" in output:
            time_match = re.search(r"time=(\d+:\d+:\d+.\d+)", output)
            if time_match:
                time = time_match.group(1)
                time_parts = time.split(":")
                current_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + float(time_parts[2])
                progress_percent = math.floor((current_seconds / total_seconds) * 100)
                bot.send_message(chat_id, f"Encoding progress: {progress_percent}%")

        bot.send_message(chat_id, output)
        

    # Clean up files
    os.remove(video_path)
    os.remove(output_path)

if __name__ == "__main__":
    bot.polling(none_stop=True)
    
