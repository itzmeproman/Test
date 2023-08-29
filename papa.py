# Import the required modules
import os
import subprocess
import telebot
from telebot import types

# Load the environment variables
DOWNLOAD_DIR = os.environ.get('DOWNLOAD_DIR') or 'downloads'
WATERMARK = os.environ.get('WATERMARK') or '@aniimax'

# Set the bot token, API ID, and API hash
BOT_TOKEN = '6154222206:AAFxkaTRgMI52biIT3m4qAUDwsWIySnoY2c'
API_ID = 20210345
API_HASH = '11bcb58ae8cfb85168fc1f2f8f4c04c2'

# Create the bot object
bot = telebot.TeleBot(BOT_TOKEN)

# Define a handler for the /start command
@bot.message_handler(commands=['start'])
def start(message):
    # Send a welcome message
    bot.send_message(message.chat.id, 'Hello, I am a video encoder bot. I can convert your videos to 480p using ffmpeg and add a watermark of ' + WATERMARK + '. Send me a video file to start.')

# Define a handler for video messages
@bot.message_handler(content_types=['video'])
def encode(message):
    # Get the video file information
    video = message.video
    file_id = video.file_id
    file_name = video.file_name or file_id + '.mp4'
    file_size = video.file_size

    # Send a message to acknowledge the video
    bot.send_message(message.chat.id, 'I received your video. It has a file size of ' + str(file_size) + ' bytes. I will start encoding it soon.')

    # Download the video file to the local directory
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    downloaded_file = bot.download_file(file_path)
    with open(os.path.join(DOWNLOAD_DIR, file_name), 'wb') as new_file:
        new_file.write(downloaded_file)

    # Create the output file name and path
    output_file_name = file_id + '_480p.mp4'
    output_file_path = os.path.join(DOWNLOAD_DIR, output_file_name)

    # Create the ffmpeg command to encode the video to 480p and add the watermark using a faster preset and a higher CRF value
    ffmpeg_command = ['ffmpeg', '-i', os.path.join(DOWNLOAD_DIR, file_name), '-vf', 'scale=-2:480,drawtext=text=' + WATERMARK + ':fontcolor=white:fontsize=24:x=w-tw-10:y=h-th-10', '-c:v', 'libx264', '-crf', '30', '-preset', 'veryfast', '-c:a', 'copy', output_file_path]

    # Run the ffmpeg command as a subprocess and capture the output
    process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    # Define a function to parse the ffmpeg output and get the progress percentage
    def get_progress(output):
        # Find the duration of the video from the output
        duration = 0.0
        for line in output.split('\n'):
            if 'Duration' in line:
                time_str = line.split()[1].strip(',')
                hours, minutes, seconds = map(float, time_str.split(':'))
                duration = hours * 3600 + minutes * 60 + seconds
                break

        # Find the current time of the encoding from the output
        current_time = 0.0
        for line in reversed(output.split('\n')):
            if 'time=' in line:
                time_str = line.split()[3].strip('time=')
                hours, minutes, seconds = map(float, time_str.split(':'))
                current_time = hours * 3600 + minutes * 60 + seconds
                break

        # Calculate and return the progress percentage
        if duration > 0:
            progress = round((current_time / duration) * 100, 2)
            return progress
        else:
            return 0.0

    # Initialize an empty output string and a progress variable
    output = ''
    progress = 0.0

    # Loop until the subprocess is finished
    while True:
        # Read a line from the subprocess output
        line = process.stdout.readline()

        # Break the loop if the subprocess is done
        if not line:
            break

        # Append the line to the output string
        output += line

        # Get the current progress percentage from the output string
        current_progress = get_progress(output)

        # If the current progress is greater than the previous progress, send an update message
        if current_progress > progress:
            progress = current_progress
            bot.send_message(message.chat.id, 'Encoding progress: ' + str(progress) + '%')

    # Send a message to indicate the encoding is finished
    bot.send_message(message.chat.id, 'Encoding finished. I will send you the encoded video file soon.')

    # Send the encoded video file to the user
    with open(output_file_path, 'rb') as encoded_file:
        bot.send_video(message.chat.id, encoded_file, supports_streaming=True)

    # Delete the original and encoded video files from the local directory
    os.remove(os.path.join(DOWNLOAD_DIR, file_name))
    os.remove(output_file_path)

# Start polling for updates
bot.polling()

