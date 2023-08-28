import os
import subprocess
import threading
import time
from pyrogram import Client, filters
from pyrogram.types import Message

# Define the bot token and API keys
API_ID = os.environ.get("20210345")
API_HASH = os.environ.get("11bcb58ae8cfb85168fc1f2f8f4c04c2")
BOT_TOKEN = os.environ.get("6154222206:AAFxkaTRgMI52biIT3m4qAUDwsWIySnoY2c")

# Create a bot instance
bot = Client("video_encoder_bot", api_id=20210345, api_hash=0x11bcb58ae8cfb85168fc1f2f8f4c04c2, bot_token="6154222206:AAFxkaTRgMI52biIT3m4qAUDwsWIySnoY2c")

# Define the download directory and the ffmpeg command
DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "downloads/")
FFMPEG_CMD = "ffmpeg -i {input} -c:v libx264 -crf 26 -vf scale=-2:480 {output}"

# Define a global variable to store the encoding progress
progress = 0

# Define a function to update the progress variable
def update_progress(process):
    global progress
    while True:
        # Read the output of the ffmpeg process
        output = process.stderr.readline().decode()
        # If the output is empty, break the loop
        if output == "":
            break
        # If the output contains "time=", extract the current time
        if "time=" in output:
            time_string = output.split("time=")[1].split()[0]
            # Convert the current time to seconds
            current_time = sum(float(x) * 60 ** i for i, x in enumerate(reversed(time_string.split(":"))))
            # Calculate the progress percentage
            progress = round((current_time / total_time) * 100, 2)
        # Sleep for one second
        time.sleep(1)

# Define a function to encode a video file
def encode_video(file_path):
    # Get the file name and extension
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_name)[1]
    # Generate a new file name with ".480p" suffix
    new_file_name = file_name.replace(file_ext, f".480p{file_ext}")
    # Generate the input and output file paths
    input_file = os.path.join(DOWNLOAD_DIR, file_name)
    output_file = os.path.join(DOWNLOAD_DIR, new_file_name)
    # Get the total duration of the video file in seconds
    global total_time
    total_time = str(total_time)
d # Run the ffmpeg command in a subprocess
    process = subprocess.Popen(FFMPEG_CMD.format(input=input_file, output=output_file), shell=True, stderr=subprocess.PIPE)
    # Create a thread to update the progress variable
    thread = threading.Thread(target=update_progress, args=(process,))
    thread.start()
    # Wait for the process to complete
    process.wait()
    # Return the output file path
    return output_file

# Define a handler for the /start command
@bot.on_message(filters.command("start"))
def start(bot, message):
    # Send a welcome message to the user
    message.reply_text("Hello, I am a video encoder bot. I can convert your videos to 480p resolution using ffmpeg. Just send me any video file and I will do the rest.")

# Define a handler for video files
@bot.on_message(filters.video)
def video(bot, message):
    # Send a message to the user indicating the download process
    message.reply_text("Downloading your video file...")
    # Download the video file to the download directory
    file_path = message.download(file_name=DOWNLOAD_DIR)
    # Send a message to the user indicating the encoding process
    message.reply_text("Encoding your video file...")
    # Encode the video file and get the output file path
    output_file = encode_video(file_path)
    # Send a message to the user indicating the upload process with a progress bar
    message.reply_text("Uploading your video file...", reply_markup=progress_bar())
    # Upload the output file as a video with a thumbnail and a caption
    message.reply_video(output_file, thumb=file_path, caption=f"Encoded by @video_encoder_bot")
    # Delete the input and output files from the download directory
    os.remove(file_path)
    os.remove(output_file)

# Define a function to generate a progress bar with the current progress percentage
def progress_bar():
    # Define the symbols for the progress bar
    fill_char = "█"
    empty_char = "░"
    # Define the length of the progress bar
    bar_length = 10
    # Calculate the number of filled and empty symbols based on the progress percentage
    filled = int(progress / 10)
    empty = bar_length - filled
    # Generate the progress bar string
    bar = fill_char * filled + empty_char * empty
    # Return the progress bar as an inline keyboard with a callback data of "None"
    return InlineKeyboardMarkup([[InlineKeyboardButton(f"{bar} {progress}%", callback_data="None")]])

# Define a handler for the callback queries
@bot.on_callback_query()
def callback(bot, update):
    # Ignore the callback queries as they are just for showing the progress bar
    pass

# Run the bot
bot.run()
    
