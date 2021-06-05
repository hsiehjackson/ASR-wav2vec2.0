import collections
import webrtcvad
import numpy as np
from asr import ASRtranscribe
from vad import VoiceActivityDetection

class ASRstream(object):
    def __init__(self, w2v_path, dict_path, vad_path, device, sample_rate):
        self.ASRtranscribe = ASRtranscribe(w2v_path, dict_path, vad_path, device)
        self.vad = VoiceActivityDetection(vad_path, device)
        self.slide_window = collections.deque(maxlen=5)
        self.triggered = False
        self.voiced_frames = []
        self.sample_rate = sample_rate
    
    def streaming_recognize(self, frames):
        for frame in frames:
            frame_np = np.fromstring(frame, dtype=np.float32)
            is_speech = self.vad.is_speech(frame_np, self.sample_rate)
            is_speech = collections.Counter(is_speech).most_common()[0][0]
            # print(is_speech)
            if not self.triggered:
                self.slide_window.append((frame, is_speech))
                num_voiced = len([f for f, speech in self.slide_window if speech])
                if num_voiced > 0.5 * self.slide_window.maxlen:
                    self.triggered = True
                    self.voiced_frames = [f for f,s in self.slide_window]
                    self.slide_window.clear()
            else:
                self.voiced_frames.append(frame)
                self.slide_window.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in self.slide_window if not speech])
                
                if num_unvoiced > 0.9 * self.slide_window.maxlen:
                    response = {}
                    total_frames =  b''.join(self.voiced_frames)
                    signal = np.fromstring(total_frames, dtype=np.float32)
                    results = self.ASRtranscribe(signal, stream=True)['results']

                    if len(results) > 0:
                        response['transcript'] = results[0]['speech']
                    response['is_final'] = True
                    self.triggered = False
                    self.slide_window.clear()
                    self.voiced_frames = []
                    self.triggered = False

                    yield response
                