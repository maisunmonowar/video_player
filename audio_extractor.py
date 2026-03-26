import subprocess
import os

class AudioExtractor:
    @staticmethod
    def extract_audio(video_path: str, output_audio_path: str = "temp_audio.wav") -> str:
        """
        Extracts audio from a video file and saves it as a temporary WAV file.
        Returns the path to the extracted audio file.
        """
        if os.path.exists(output_audio_path):
            os.remove(output_audio_path)
            
        command = [
            "ffmpeg",
            "-i", video_path,
            "-vn",          # No video
            "-acodec", "pcm_s16le", # 16-bit PCM
            "-ar", "16000", # 16kHz for whisper
            "-ac", "1",     # Mono channel
            "-y",           # Overwrite output
            output_audio_path
        ]
        
        print(f"Running command: {' '.join(command)}")
        try:
            # We use subprocess directly to avoid extra python wrappers, it's reliable
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Audio extraction successful.")
            return output_audio_path
        except subprocess.CalledProcessError as e:
            print(f"Error extracting audio: {e.stderr.decode()}")
            raise e
