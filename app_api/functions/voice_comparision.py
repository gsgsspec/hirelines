import os
import requests

import numpy as np
from urllib.parse import urlparse



from hirelines import settings
from app_api.models import CallSchedule


def convertProfilingVideo(video_url, schedule_id):
    try:

        import ffmpeg

        call_details = CallSchedule.objects.get(id=schedule_id)

        file_name = f"{call_details.id}_profileaudio.wav"

        profiling_dir = os.path.join(settings.MEDIA_ROOT, "uploads","candidate_audio")
        os.makedirs(profiling_dir, exist_ok=True)

        parsed_url = urlparse(video_url)
        filename = os.path.basename(parsed_url.path)
        video_path = os.path.join(profiling_dir, filename)

        wav_path = os.path.join(profiling_dir, file_name)

        # Checking if already profiling audio exists
        if os.path.exists(wav_path):
            print(f"File already converted: {wav_path}")
            return wav_path

        # Download the video
        response = requests.get(video_url, stream=True)
        if response.status_code != 200:
            raise Exception(f"Failed to download video")

        # Save the video locally
        with open(video_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Converting video to WAV format using FFmpeg
        ffmpeg.input(video_path).output(wav_path, format="wav", acodec="pcm_s16le", ar="44100").run(overwrite_output=True)

        # Deleting video file after converting to wav file
        os.remove(video_path)

    except Exception as e:
        print(f"Error: {e}")
        raise


def compareVoices(file1,file2):
    try:

        from resemblyzer import preprocess_wav, VoiceEncoder

        if not file1.endswith(".wav"):
            file1 = convert_audio_to_wav(file1)
        if not file2.endswith(".wav"):
            file2 = convert_audio_to_wav(file2)

        encoder = VoiceEncoder()

        # Preprocess the WAV files and obtain embeddings
        wav1 = preprocess_wav(file1)
        wav2 = preprocess_wav(file2)

        # Get voice embeddings for both samples
        embedding1 = encoder.embed_utterance(wav1)
        embedding2 = encoder.embed_utterance(wav2)

        # Calculate cosine similarity between the embeddings
        similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
        similarity_percentage = similarity * 100

        print(f"Similarity between the voices: {similarity_percentage:.2f}%")

        return similarity_percentage


    except Exception as e:
        print(str(e))
        raise


def convert_audio_to_wav(target_file_path: str):
    try:

        from pydub import AudioSegment

        # Load audio
        audio = AudioSegment.from_file(target_file_path)
        wav_file = target_file_path.split('.')[0] + ".wav"
        audio.export(wav_file, format="wav")
        return wav_file
    except Exception as e:
        print(f"Error converting file: {e}")
        return None