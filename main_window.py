import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QSlider, QFileDialog, QStyle, QLabel,
    QInputDialog, QSizePolicy, QGraphicsView, QGraphicsScene
)
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal, QThread, QObject, QSizeF
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem

from audio_extractor import AudioExtractor
from transcriber import Transcriber
from translator import Translator

class VideoGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.video_item = QGraphicsVideoItem()
        self.setScene(QGraphicsScene(self))
        self.scene().addItem(self.video_item)
        self.setStyleSheet("background-color: black; border: none;")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.scene().setSceneRect(0, 0, self.viewport().width(), self.viewport().height())
        self.video_item.setSize(QSizeF(self.viewport().width(), self.viewport().height()))

class ProcessingWorker(QThread):
    finished = pyqtSignal(list, list) # original_segments, translated_segments
    error = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, video_path: str, target_lang: str):
        super().__init__()
        self.video_path = video_path
        self.target_lang = target_lang

    def run(self):
        try:
            self.status_update.emit("Extracting audio...")
            audio_path = AudioExtractor.extract_audio(self.video_path)
            
            self.status_update.emit("Transcribing audio (this might take a while)...")
            transcriber = Transcriber()
            original_lang, original_segments = transcriber.transcribe(audio_path)
            
            self.status_update.emit(f"Detected original language: {original_lang}. Translating to {self.target_lang}...")
            translator = Translator()
            translated_segments = translator.translate_segments(original_segments, original_lang, self.target_lang)
            
            # Clean up temp audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)
                
            self.finished.emit(original_segments, translated_segments)
            
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dual-Subtitle Video Player")
        self.resize(1024, 600)

        # Main Widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Video Container for Layout Overlays
        self.video_container = QWidget(self)
        self.video_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # We use a QGridLayout to place labels on strictly top of video
        # by sharing the same grid space.
        self.overlay_layout = QGridLayout(self.video_container)
        self.overlay_layout.setContentsMargins(0, 0, 0, 0)
        self.overlay_layout.setRowStretch(0, 1)
        self.overlay_layout.setColumnStretch(0, 1)

        # Video Player and Video Widget
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.media_player.setAudioOutput(self.audio_output)
        
        self.video_widget = VideoGraphicsView()
        self.media_player.setVideoOutput(self.video_widget.video_item)

        # Subtitle Labels (No parent passed explicitly to let layout handle it)
        self.top_subtitle_label = QLabel("")
        self.top_subtitle_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.top_subtitle_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold; background-color: rgba(0, 0, 0, 150); padding: 5px;")
        self.top_subtitle_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.top_subtitle_label.setWordWrap(True)
        
        self.bottom_subtitle_label = QLabel("")
        self.bottom_subtitle_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        self.bottom_subtitle_label.setStyleSheet("color: yellow; font-size: 20px; font-weight: bold; background-color: rgba(0, 0, 0, 150); padding: 5px;")
        self.bottom_subtitle_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.bottom_subtitle_label.setWordWrap(True)

        self.overlay_layout.addWidget(self.video_widget, 0, 0)
        self.overlay_layout.addWidget(self.top_subtitle_label, 0, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.overlay_layout.addWidget(self.bottom_subtitle_label, 0, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)

        # Controls
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.clicked.connect(self.toggle_play)

        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)

        self.open_button = QPushButton("Open Video...")
        self.open_button.clicked.connect(self.open_file)

        # Status Label
        self.status_label = QLabel("Ready")

        # Layout Setup
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(10, 10, 10, 10)
        control_layout.addWidget(self.open_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.position_slider)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_container)
        main_layout.addWidget(self.status_label)
        main_layout.addLayout(control_layout)

        self.central_widget.setLayout(main_layout)

        # Media Player Signals
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.mediaStatusChanged.connect(self.media_status_changed)

        # Subtitle Data 
        self.original_subs = []
        self.translated_subs = []

    def toggle_play(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            self.media_player.play()
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def set_position(self, position):
        self.media_player.setPosition(position)

    def position_changed(self, position):
        self.position_slider.setValue(position)
        self.update_subtitles(position / 1000.0) # convert to seconds

    def duration_changed(self, duration):
        self.position_slider.setRange(0, duration)

    def media_status_changed(self, status):
        # Reset play button when video ends
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def open_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        file_dialog.setWindowTitle("Open Video File")
        file_dialog.setNameFilter("Video Files (*.mp4 *.mkv *.avi *.mov *.wmv)")
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.start_processing_pipeline(file_path)

    def start_processing_pipeline(self, file_path):
        target_lang, ok = QInputDialog.getText(self, "Target Language", "Enter the target language code for translation (e.g., 'es', 'fr', 'en'):")
        if not ok or not target_lang:
            target_lang = "en" # default to english

        self.status_label.setText(f"Loading video: {os.path.basename(file_path)} | Target Lang: {target_lang}")
        
        # Load Video into Player
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        
        # Disable playback until processed
        self.play_button.setEnabled(False)
        self.top_subtitle_label.setText("")
        self.bottom_subtitle_label.setText("")
        
        self.worker = ProcessingWorker(file_path, target_lang)
        self.worker.status_update.connect(lambda msg: self.status_label.setText(msg))
        self.worker.error.connect(lambda err: self.status_label.setText(f"Error: {err}"))
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.start()

    def on_processing_finished(self, original, translated):
        self.original_subs = original
        self.translated_subs = translated
        self.status_label.setText("Processing complete. Ready to play.")
        self.play_button.setEnabled(True)

    def update_subtitles(self, time_sec):
        # Update original subtitle (bottom)
        current_orig = ""
        for seg in self.original_subs:
            if seg["start"] <= time_sec <= seg["end"]:
                current_orig = seg["text"]
                break
        self.bottom_subtitle_label.setText(current_orig)
        self.bottom_subtitle_label.raise_()
        
        # Update translated subtitle (top)
        current_trans = ""
        for seg in self.translated_subs:
            if seg["start"] <= time_sec <= seg["end"]:
                current_trans = seg["text"]
                break
        self.top_subtitle_label.setText(current_trans)
        self.top_subtitle_label.raise_()

