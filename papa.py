import os
import subprocess
import threading
import time
import tgcrypto # Import tgcrypto
from pyrogram import Client, filters
from pyrogram.types import Message

# Define the bot token and API keys
API_ID = os.environ.get("20210345")
API_HASH = os.environ.get("11bcb58ae8cfb85168fc1f2f8f4c04c2")
BOT_TOKEN = os.environ.get("6154222206:AAFxkaTRgMI52biIT3m4qAUDwsWIySnoY2c")

# Create a bot instance
bot = Client("video_encoder_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

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
    total_time = float(total_time)
    
    # Generate a random key and iv for encryption
    key = os.urandom(32)
    iv = os.urandom(16)

    # Read the video file as bytes
    with open(input_file, "rb") as f:
        data = f.read()

    # Encrypt the data using tgcrypto AES-256-CTR mode
    encrypted_data = tgcrypto.ctr256_encrypt(data, key, iv, bytes(1))

    # Write the encrypted data to a temporary file
    with open("temp.mp4", "wb") as f:
        f.write(encrypted_data)

    # Run the ffmpeg command in a subprocess on the temporary file
    process = subprocess.Popen(FFMPEG_CMD.format(input="temp.mp4", output=output_file), shell=True, stderr=subprocess.PIPE)
    
    # Delete the temporary file
    os.remove("temp.mp4")

    # Create a thread to update the progress variable
    thread = threading.Thread(target=update_progress, args=(process,))
    thread.start()
    # Wait for the process to complete
    process.wait()
    
    # Read the output file as bytes
    with open(output_file, "rb") as f:
        data = f.read()

    # Decrypt the data using tgcrypto AES-256-CTR mode
    decrypted_data = tgcrypto.ctr256_decrypt(data, key, iv, bytes(1))

    # Write the decrypted data to the output file
    with open(output_file, "wb") as f:
        f.write(decrypted_data)

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

# Define a function to generate a progress bar with the current progress
def progress_bar():
    # Create a string of 10 characters representing the progress bar
    # Use "#" for filled parts and "-" for empty parts
    bar = "#" * int(progress / 10) + "-" * (10 - int(progress / 10))
    # Return the progress bar string with the percentage
    return f"[{bar}] {progress}%"
    
