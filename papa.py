# Import the required modules
import os
import telebot
import ffmpeg
import pymongo
from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv()

# Get the bot token, API ID, API hash and database URL from environment variables
BOT_TOKEN = os.getenv("6154222206:AAFxkaTRgMI52biIT3m4qAUDwsWIySnoY2c")
API_ID = os.getenv("20210345")
API_HASH = os.getenv("11bcb58ae8cfb85168fc1f2f8f4c04c2")
DB_URL = os.getenv("mongodb+srv://papapandey:itzmeproman@itzmeproman1.obpzbn7.mongodb.net/?retryWrites=true&w=majority")

# Create a telebot instance
bot = telebot.TeleBot(BOT_TOKEN)

# Create a mongodb client and connect to the database
client = pymongo.MongoClient(DB_URL)
db = client["video_encoder_bot"]
collection = db["videos"]

# Define a function to encode a video file using ffmpeg
def encode_video(file_path, output_path):
    # Set the output resolution to 480p
    resolution = "480x270"
    # Create a ffmpeg input object from the file path
    input = ffmpeg.input(file_path)
    # Create a ffmpeg output object with the output path and resolution
    output = ffmpeg.output(input, output_path, vf=f"scale={resolution}")
    # Run the ffmpeg command and return the process object
    process = ffmpeg.run_async(output, pipe_stdout=True, pipe_stderr=True)
    return process

# Define a function to get the progress percentage of a process
def get_progress(process):
    # Initialize the progress percentage to zero
    progress = 0
    # Read the standard output and standard error of the process
    stdout, stderr = process.communicate()
    # If there is standard error, parse it for the duration and time information
    if stderr:
        stderr = stderr.decode("utf-8")
        duration = None
        time = None
        # Loop through each line of the standard error
        for line in stderr.split("\n"):
            # If the line contains "Duration", extract the duration value in seconds
            if "Duration" in line:
                duration = line.split(",")[0].split(":")[1:]
                duration = int(duration[0]) * 3600 + int(duration[1]) * 60 + float(duration[2])
            # If the line contains "time", extract the time value in seconds
            if "time" in line:
                time = line.split("=")[1].split(" ")[0].split(":")
                time = int(time[0]) * 3600 + int(time[1]) * 60 + float(time[2])
        # If both duration and time are available, calculate the progress percentage as time / duration * 100
        if duration and time:
            progress = round(time / duration * 100, 2)
    # Return the progress percentage
    return progress

# Define a handler function for the /start command
@bot.message_handler(commands=["start"])
def start(message):
    # Send a welcome message to the user
    bot.send_message(message.chat.id, f"Hello {message.from_user.first_name}, I am a video encoder bot. I can convert your videos to 480p resolution using ffmpeg. To use me, just send me a video file and I will do the rest.")

# Define a handler function for video messages
@bot.message_handler(content_types=["video"])
def video(message):
    # Send a message to the user that the video is being downloaded
    bot.send_message(message.chat.id, "Downloading your video...")
    # Get the file ID of the video message
    file_id = message.video.file_id
    # Get the file information of the video message
    file_info = bot.get_file(file_id)
    # Get the download link of the video file
    download_link = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
    # Download the video file and save it locally with a unique name based on the file ID
    download_path = f"{file_id}.mp4"
    bot.download_file(file_info.file_path, download_path)
    # Send a message to the user that the video has been downloaded and is being encoded
    bot.send_message(message.chat.id, "Video downloaded. Encoding your video...")
    # Encode the video file using ffmpeg and get the process object
    output_path = f"{file_id}_480p.mp4"
    process = encode_video(download_path, output_path)
    # Get the progress percentage of the encoding process
    progress = get_progress(process)
    # Send a message to the user with the initial progress percentage
    progress_message = bot.send_message(message.chat.id, f"Encoding progress: {progress}%")
    # Loop until the encoding process is finished or failed
    while progress < 100 and process.returncode is None:
        # Update the progress percentage of the encoding process
        progress = get_progress(process)
        # Edit the progress message with the updated progress percentage
        bot.edit_message_text(f"Encoding progress: {progress}%", message.chat.id, progress_message.message_id)
    # If the encoding process is successful, send a message to the user that the video has been encoded and is being uploaded
    if process.returncode == 0:
        bot.send_message(message.chat.id, "Video encoded. Uploading your video...")
        # Upload the encoded video file to the user
        bot.send_video(message.chat.id, open(output_path, "rb"))
        # Send a message to the user that the video has been uploaded
        bot.send_message(message.chat.id, "Video uploaded. Enjoy!")
        # Save the video information to the database
        collection.insert_one({"user_id": message.from_user.id, "file_id": file_id, "download_path": download_path, "output_path": output_path})
    # If the encoding process is failed, send a message to the user that an error occurred
    else:
        bot.send_message(message.chat.id, "An error occurred while encoding your video. Please try again later.")
    # Delete the downloaded and encoded video files from the local storage
    os.remove(download_path)
    os.remove(output_path)

# Start polling for updates from Telegram
bot.polling()


