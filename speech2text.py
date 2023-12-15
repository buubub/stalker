from datetime import  timedelta
import os
import whisper

def get_user_transcript(recordTimetamp, username, file):
    userTranscript = {}
    model = whisper.load_model("small")
    transcription = model.transcribe(file, fp16=False)

    for transcript in transcription['segments']:
        second = int(transcript['start'])
        microsecond = int((transcript['start'] - second) * 1e6)
        delta = timedelta(seconds=second, microseconds=microsecond)
        timestamp = recordTimetamp + delta

        key = f"{timestamp.strftime('%H:%M:%S.%f')} @{username}"
        userTranscript.update({key: transcript['text'].strip()})

    return userTranscript

def compile_user_transcript(userTranscripts, dir):
    with open(os.path.join(dir, 'transcript.txt'), 'w') as file:
        for timestamp, text in userTranscripts:
            file.write(f'{timestamp}: {text}\n')
