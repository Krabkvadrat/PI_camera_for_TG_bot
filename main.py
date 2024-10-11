
# - *- coding: utf- 8 - *-
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from time import sleep
import telebot
from datetime import datetime
import os 
import subprocess


from settings import token

bot = telebot.TeleBot(token)

directory = os.path.dirname(os.path.abspath(__file__))

directory_image = directory + '/images/' 
os.makedirs(directory_image, exist_ok=True)

directory_video = directory + '/videos/' 
os.makedirs(directory_video, exist_ok=True)

def convert_h264_to_mp4(input_file: str, output_file: str):
    """
    Convert an H.264 file to MP4 format using ffmpeg and delete the original H.264 file after conversion.

    Parameters:
    input_file (str): The path to the input H.264 file.
    output_file (str): The path to the output MP4 file.
    """
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"The input file {input_file} does not exist.")

    command = [
        'ffmpeg',
        '-fflags', '+genpts',    # Generate presentation timestamps
        '-i', input_file,        # Input file
        '-c:v', 'copy',          # Copy the video codec (no re-encoding)
        '-c:a', 'aac',           # Use AAC codec for audio
        '-b:a', '192k',          # Set audio bitrate
        output_file              # Output file
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Successfully converted {input_file} to {output_file}.")

        # Delete the original H.264 file after successful conversion
        os.remove(input_file)
        print(f"Deleted the original file: {input_file}.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during conversion: {e}")
    except OSError as e:
        print(f"Error deleting file: {e}")

def send_last_file(path, message, file_type):
    try:
        # List files and sort them by modification time (most recent last)
        files = os.listdir(path)
        files_sorted = sorted(files)


        # Now that we've cleaned the folder, send the last file        

        link = f'{path}' +  files_sorted[-1]
        bot.send_message(message.chat.id, files_sorted[-1])
        if file_type == 'video':
            files_limit = 10
            bot.send_video(message.chat.id, video=open(link, 'rb'), supports_streaming=True)
        elif file_type == 'photo':
            files_limit = 20
            bot.send_photo(message.chat.id, photo=open(link,'rb'))       

        # Delete all but the {files_limit} most recent files
        n_files = len(files_sorted)
        indx = n_files - files_limit
        if n_files > 10:
            for file in files_sorted[0:indx]:
                os.remove(os.path.join(path, file))
                
    except Exception as _ex:
        print(f"{_ex},/nError sending file")

        

@bot.message_handler(commands=['start'])
def send_welcome(message):
#	user_id = message.from_user.id
#	user_name = message.from_user.username
    bot.send_message(message.chat.id, "Hello!")

@bot.message_handler(commands=['video'])
def send_welcome(message):
    try: 
 
        now = datetime.now().strftime('%Y%m%d_%H_%M_%S')
        output_file = f"{directory_video}{now}_now.h264"
        output_file_converted = f"{directory_video}{now}_now.mp4"

        picam2 = Picamera2()

        video_config = picam2.create_video_configuration()
        video_config["size"] = (800, 600)  
        picam2.configure(video_config)
    
        encoder = H264Encoder(10000000)

        picam2.start_recording(encoder, output_file)
        bot.send_message(message.chat.id, f"recording 10 sec video")

        sleep(10)
        picam2.stop_recording()
        picam2.close()
        convert_h264_to_mp4(output_file,output_file_converted)
        bot.send_message(message.chat.id, f"video ready")
        send_last_file(directory_video, message, 'video')

    except Exception as _ex:
        bot.send_message(message.chat.id, f"{_ex}\nsomething wrong")

@bot.message_handler(commands=['show_video'])
def send_video(message):
    try:     
        send_last_file(directory_video, message, 'video')
    except:
        bot.send_message(message.chat.id, "/nError sending video")

@bot.message_handler(commands=['camera'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Capturing photo")
    try:      
        picam2 = Picamera2()
        now = datetime.now().strftime('%Y%m%d_%H_%M_%S')
        preview_config = picam2.create_preview_configuration(main={"size": (800, 600)})
        picam2.configure(preview_config) 
        picam2.start()
        sleep(2)
        picam2.capture_file(f'{directory_image}{now}.jpg')
        bot.send_message(message.chat.id, f"Photo captured")
        picam2.close()
        send_last_file(directory_image, message, 'photo')

    except Exception as _ex:
        bot.send_message(message.chat.id, f"{_ex}\nSome error while doing making photo")
        
 
@bot.message_handler(commands=['photo'])
def send_welcome(message):
    try:     
        send_last_file(directory_image, message, 'photo')
    except:
        bot.send_message(message.chat.id, "Error sending photo")
 
 

@bot.message_handler(commands=['num'])
def cmd_city(message):
    send = bot.send_message(message.chat.id, 'Р’РІРµРґРё РЅРѕРјРµСЂ С„РѕС‚Рѕ')
    bot.register_next_step_handler(send, city)

def city(message):
    try:
        photo = f'{directory_image}' + message.text
        bot.send_photo(message.chat.id, photo=open(photo,'rb')) 
    except:
        bot.send_message(message.chat.id, "РћС€РёР±РєР°")
 

print('TG bot started')
bot.infinity_polling()




