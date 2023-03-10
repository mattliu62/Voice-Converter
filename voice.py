import sounddevice as sd
import soundfile
import speech_recognition as sr
from scipy.io.wavfile import write
from pynput import keyboard
from pynput.mouse import Listener
import requests
from voicevox import Client
import asyncio
import os
# from playsound import playsound
import pygame


fs = 44100  # Sample rate
seconds = 10  # Duration of recording
filename = "output.wav"  # Name of output file

r = sr.Recognizer()

url = 'http://127.0.0.1:5000/translate'  # Replace with your server's URL
headers = {'Content-type': 'application/json'}


def on_press(key):
    if key == keyboard.Key.esc:
        print("Quitting program...")
        quit()

async def v_voice(text):
    async with Client() as client:

        #3, 6, 
        audio_query = await client.create_audio_query(
            text, speaker=6
        )
        with open("voice.wav", "wb") as f:
            f.write(await audio_query.synthesis())
        # playsound('voice.wav')

        import pygame

        # initialize pygame
        pygame.init()

        # load audio file
        audio_file = 'voice.wav'
        pygame.mixer.music.load(audio_file)

        # play audio file twice
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pass # wait for audio to finish playing

        # quit pygame
        pygame.quit()




def on_click(x, y, button, pressed):
    global recording
    
    if button == button.middle:
        if pressed:
            print("Recording started...")
            recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
        else:
            print("Recording stopped.")
            sd.stop()  # Stop the recording
            write(filename, fs, recording)  # Save the recording to file

            data, samplerate = soundfile.read('output.wav')
            soundfile.write('output.wav', data, samplerate, subtype='PCM_16')
            wave = sr.AudioFile('output.wav')
            with wave as source:
                audio = r.record(source)
            # try:
                s = r.recognize_google(audio)
                data = {'q': s, 'source': 'en', 'target': 'ja', 'format' : 'text', 'api_key': ""}
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    translation = response.json()['translatedText']
                    
                    #English
                    print(s)

                    #Japanese
                    print(translation)

                    asyncio.run(v_voice(translation))

                else:
                    print(f"Error: {response.status_code}")


            # except Exception as e:
            #     print("Exception: "+str(e))

with Listener(on_click=on_click) as listener:
    listener.join()
