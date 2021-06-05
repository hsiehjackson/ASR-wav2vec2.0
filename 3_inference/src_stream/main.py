from __future__ import division

import re
import sys
import pyaudio
import numpy as np
from six.moves import queue

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import webrtcvad
# Audio recording parameters
RATE = 16000
DURATION = 100 #ms
CHUNK = int(RATE * (DURATION / 1000))

import torch
from asr_stream import ASRstream


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        print('Start Microphone...')
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            # while True:
            #     try:
            #         chunk = self._buff.get(block=False)
            #         if chunk is None:
            #             return
            #         data.append(chunk)
            #     except queue.Empty:
            #         break
            yield b"".join(data)


def listen_print_loop(responses):
    num_chars_printed = 0
    for response in responses:
        if 'transcript' not in response:
            continue

        transcript = response['transcript']
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if 'is_final' not in response:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()
            num_chars_printed = len(transcript)

        else:
            print(transcript + overwrite_chars)
            num_chars_printed = 0

# import collections
# from vad import VoiceActivityDetection
# vad = VoiceActivityDetection('./models/vad.pt', torch.device("cuda" if torch.cuda.is_available() else "cpu"))
# def test(frames):
#     for frame in frames:
#         frame_16 = np.fromstring(frame, dtype=np.float32)
#         # print(len(frame))
#         # print(len(frame_16))
#         is_speech = vad.is_speech(frame_16, RATE)
#         is_speech = collections.Counter(is_speech).most_common()[0][0]
#         print(is_speech)

def main():
    w2v_path = '3_inference/models/wav2vec.pt'
    dict_path = '3_inference/models/dict.ltr.txt'
    vad_path = '3_inference/models/vad.pt'
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ASR = ASRstream(
        w2v_path=w2v_path,
        dict_path=dict_path,
        vad_path=vad_path,
        device=device,
        sample_rate=RATE)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        # test(audio_generator)
        responses = ASR.streaming_recognize(audio_generator)
        listen_print_loop(responses)


if __name__ == "__main__":
    main()

# 1. results { alternatives { transcript: "tube" } stability: 0.01 }
# 2. results { alternatives { transcript: "to be a" } stability: 0.01 }
# 3. results { alternatives { transcript: "to be" } stability: 0.9 } 
#    results { alternatives { transcript: " or not to be" } stability: 0.01 }
# 4. results { alternatives { transcript: "to be or not to be" confidence: 0.92 } alternatives { transcript: "to bee or not to bee" } is_final: true }
# 5. results { alternatives { transcript: " that's" } stability: 0.01 }
# 6. results { alternatives { transcript: " that is" } stability: 0.9 } 
#    results { alternatives { transcript: " the question" } stability: 0.01 }
# 7. results { alternatives { transcript: " that is the question" confidence: 0.98 } alternatives { transcript: " that was the question" } is_final: true }