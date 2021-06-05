"""Automatic Speech Recognition related modeling class"""

import logging
import os
from typing import Optional

import numpy as np
import librosa  # noqa
from pydub import AudioSegment
logging.getLogger("librosa").setLevel(logging.WARN)

from recognizer import BrainWav2Vec2Recognizer
from vad import VoiceActivityDetection


class ASRtranscribe(object):
    def __init__(self, w2v_path, dict_path, vad_path, device):
        vad_model = VoiceActivityDetection(
            model_path=vad_path,
            device=device,
        )

        model = BrainWav2Vec2Recognizer(
            model_path=w2v_path,
            dict_path=dict_path,
            vad_model=vad_model,
            device=device,
        )
        
        self._model = model
        self.SAMPLE_RATE = 16000
        self.MAX_VALUE = 32767
    
    def __call__(self, audio_path: str, **kwargs):
        return self.predict(audio_path, **kwargs)

    def _preprocess_audio(self, audio_path: str):

        audio_extension = audio_path.split('.')[-1].lower()
        assert audio_extension in (
            'wav', 'mp3', 'flac',
            'pcm'), f"Unsupported format: {audio_extension}"

        if audio_extension == 'pcm':
            signal = np.memmap(
                audio_path,
                dtype='h',
                mode='r',
            ).astype('float32')

        else:
            sample_rate = librosa.get_samplerate(audio_path)
            signal = AudioSegment.from_file(
                audio_path,
                format=audio_extension,
                frame_rate=sample_rate,
            )

            if sample_rate != self.SAMPLE_RATE:
                signal = signal.set_frame_rate(frame_rate=self.SAMPLE_RATE)

            channel_sounds = signal.split_to_mono()
            signal = np.array(
                [s.get_array_of_samples() for s in channel_sounds])[0]

        return signal / self.MAX_VALUE

    def predict(
        self,
        audio_path: str,
        **kwargs,
    ) -> dict:
        """
        Conduct speech recognition for audio in a given path
        Args:
            audio_path (str): the wav file path
            top_db (int): the threshold (in decibels) below reference to consider as silence (default: 48)
            batch_size (int): inference batch size (default: 1)
            vad (bool): flag indication whether to use voice activity detection or not, If it is False, it is split into
             dB criteria and then speech recognition is made. Applies only when audio length is more than 50 seconds.
        Returns:
            dict: result of speech recognition
        """
        top_db = kwargs.get("top_db", 48)
        batch_size = kwargs.get("batch_size", 1)
        vad = kwargs.get("batch_size", False)

        signal = self._preprocess_audio(audio_path)

        return self._model.predict(
            audio_path=audio_path,
            signal=signal,
            top_db=top_db,
            vad=vad,
            batch_size=batch_size,
        )