from importlib.resources import files
import sys
import wave
import json
import argparse
import Word as word_model
import simple_image_download.simple_image_download as simp
import time

from vosk import Model, KaldiRecognizer, SetLogLevel
from moviepy.editor import *
from bing_image_downloader import downloader
from google_images_download import google_images_download
from scrape import scrape, set_workers
from os import *
from os.path import isfile, join

# Argument setup
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", type=str, required=True, metavar="FILENAME", help="Name of audio file")
parser.add_argument("-m", "--music", required=False, action="store_true", help="Parse as music")
parser.add_argument("-s", "--song", type=str, required=False, metavar="SONG", help="Original song (if you are parsing vocals only)")
parser.add_argument("-v", "--verbose", required=False, action="store_true", help="Show verbose output (Non-verbose by default)")
args = parser.parse_args()

model_path = "./models/vosk-model-en-us-0.22"
audio_path = args.filename

# Verbose output
if(args.verbose == True):
    SetLogLevel(0)
else:
    SetLogLevel(-1)

# Make sure paths are correct
if not os.path.exists(model_path):
    print(f"[!] Please download the standard vosk-model-en-us model from https://alphacephei.com/vosk/models and unpack as {model_path}. Is it in the directory?")
    sys.exit()

if not os.path.exists(audio_path):
    print(f"[!] File '{audio_path}' doesn't exist. Is it in the directory?")
    sys.exit()

# Process model and audio
print(f"Reading vosk model '{model_path}'...")
model = Model(model_path)
print(f"[✓] '{model_path}' model was successfully read")

print(f"Reading file '{audio_path}'...")
wf = wave.open(audio_path, "rb")
print(f"[✓] '{audio_path}' file was successfully read")
# Files must be WAV and Mono track
if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
    print("[!] Audio file must be WAV format mono PCM. Try converting your audio file here: https://audio.online-convert.com/convert-to-wav")
    sys.exit()

rec = KaldiRecognizer(model, wf.getframerate())
rec.SetWords(True)
results = []

print("Processing audio file and detecting text...")
while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        part_result = json.loads(rec.Result())
        results.append(part_result)

part_result = json.loads(rec.FinalResult())
results.append(part_result)
wf.close()

words_obj = []
words = []
for sentence in results:
    if len(sentence) == 1:
        continue
    for w in sentence["result"]:
        word = word_model.Word(w)
        # Word list only
        words.append(w["word"])
        # Word list with time stamps and info
        words_obj.append(word)
# Note: the words list is already in order, so images can just be consecutively parsed
for word in words_obj:
    print(word.to_string())
# Download all the images, but make sure to remove duplicates first!
words = [*set(words)]
scrape(words)

original_dir = os.getcwd()
images_dir = os.getcwd() + "\photos\\"
clips = []
# Black screen until the first word
clips.append(ColorClip((1920, 1080), (0,0,0)).set_duration(words_obj[0].start))


for i in range(len(words_obj)):
    print("Iteration " + str(i) + ". The word is: " + words_obj[i].word)
    # Change back to parent directory, and then to individual word directory
    os.chdir(images_dir)
    os.chdir(images_dir + words_obj[i].word)
    print("Current directory = " + images_dir + words_obj[i].word)
    files = [f for f in listdir(os.getcwd()) if isfile(join(os.getcwd(), f))]


    # while len(files) == 0:
    #     os.chdir(images_dir)
    #     os.rmdir(images_dir + word_obj.word)
    #     set_workers(1)
    #     time.sleep(10)
    #     scrape(str(word_obj.word))
    # Even if there are multiple, just get one image
    current_img = files[0]
    # First word is just normal duration calculation
    if i == 0:
        duration = words_obj[0].end - words_obj[0].start
        clips.append(ImageClip(images_dir + words_obj[i].word + "\\" + current_img).set_duration(duration).resize(height=1080, width=1920))
    elif i == len(words_obj)-1:
        duration = words_obj[i].end - words_obj[i].start
        clips.append(ImageClip(images_dir + words_obj[i].word + "\\" + current_img).set_duration(duration).resize(height=1080, width=1920))
    else: 
        duration =  words_obj[i+1].start - words_obj[i].start
        clips.append(ImageClip(images_dir + words_obj[i].word + "\\" + current_img).set_duration(duration).resize(height=1080, width=1920))

# Change back to the original dir to write the file
os.chdir(original_dir)
# Create the video
concat_clips = concatenate_videoclips(clips, method="compose")
if args.music == True:
    audioclip = AudioFileClip(args.song)
else:
    audioclip = AudioFileClip(audio_path)

final_video = concat_clips.set_audio(audioclip)
final_video.write_videofile("test.mp4", fps=24, codec="h264_nvenc")


# Fetch the google image for each word
# downloader.download("'" + word.word + "'", limit=1, output_dir="images", adult_filter_off=True, filter="photo")
# response = google_images_download.googleimagesdownload() 
# arguments = {
#     "keywords": "image of the word " + word.word,
#     "limit": 1,
#     "print_urls": True,
# }
# try:
#     response.download(arguments)
# except FileNotFoundError:
#     print("SHITHEAD")
# downloader = simp.Downloader()
# downloader.search_urls(word.word, limit=1, verbose=True)
# print(downloader.get_urls())

# duration_black_screen = words_obj[i+1].start - words_obj[i].end
# clips.append(ColorClip((1920, 1080), (0,0,0)).set_duration(duration_black_screen))