import os
import speech_recognition as sr

r = sr.Recognizer()

file = os.path.join("output", "14-12-2023 080336", "259410894256209920.wav")
with sr.AudioFile(file) as source:
    audio_data = r.record(source)

text = r.recognize_google(audio_data, language="id-ID")
timestamps = [f"{int(segment.start / 1000)}:{int(segment.start / 1000) + 1}" for segment in audio_data]

results = list(zip(timestamps, text.split()))

for timestamp, text in results:
    print(f'{timestamp} {text}')
