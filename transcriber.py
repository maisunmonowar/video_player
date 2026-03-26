from faster_whisper import WhisperModel

class Transcriber:
    def __init__(self, model_size="tiny"):
        # Run on CPU with INT8 if we want cross-platform generic support
        # It's fast enough for 'tiny' model. GPU could be added based on device support later.
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def transcribe(self, audio_path: str):
        """
        Transcribes the given audio file using faster-whisper.
        Returns the detected original language, and a list of segment dictionaries.
        """
        print(f"Starting transcription of {audio_path}...")
        segments, info = self.model.transcribe(audio_path, beam_size=5)
        
        detected_language = info.language
        print(f"Detected language: {detected_language} with probability {info.language_probability}")
        
        result_segments = []
        for segment in segments:
            # We construct a simple dictionary with start, end, and text
            result_segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            })
            
        print("Transcription complete.")
        return detected_language, result_segments
