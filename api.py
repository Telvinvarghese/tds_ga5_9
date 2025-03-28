from fastapi import FastAPI, UploadFile, File, Query
import shutil
import speech_recognition as sr
import os
from pydub import AudioSegment

app = FastAPI()

def extract_audio_from_video(video_path, start_sec, end_sec, output_audio_path="temp_audio.wav"):
    """Extracts audio from a video segment using pydub."""
    audio = AudioSegment.from_file(video_path)[start_sec * 1000:end_sec * 1000]
    audio.export(output_audio_path, format="wav")

def transcribe_audio(audio_filename="temp_audio.wav"):
    """Transcribes the audio file using Google Web Speech API."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_filename) as source:
        audio = recognizer.record(source)
    
    try:
        transcript = recognizer.recognize_google(audio)
        return transcript
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...), start: float = Query(...), end: float = Query(...)):
    """Upload video and process transcription."""
    video_path = f"temp_{file.filename}"
    
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    audio_path = "temp_audio.wav"
    extract_audio_from_video(video_path, start, end, audio_path)
    transcript = transcribe_audio(audio_path)
    
    os.remove(video_path)
    os.remove(audio_path)
    
    return {"transcript": transcript}
