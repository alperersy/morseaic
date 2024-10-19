# audio_input
## only supports recording files for now
### only supports mono audio (CHANNEL = 1)

import pyaudio
import wave
import keyboard
import os

# User will decide these parameters through the GUI

SAMPLE_RATE = int(input("Sample Rate: (e.g 44100): "))
# RECORDING_SECS = int(input("Recording time: "))

# Static parameters

FORMAT = pyaudio.paInt16 # Bit-depth ## paInt8 => 16-bit PCM (Pulse Code Modulation)
CHANNELS = 1 # mono
CHUNK = 1024 # Number of samples per each recording loop
TEMP_REC_FILENAME = "temp_rec_mct.wav"

p = pyaudio.PyAudio() # Initialize PortAudio

# Starting the audio stream

audio_stream = p.open(format = FORMAT,
                      channels = CHANNELS,
                      rate = SAMPLE_RATE,
                      input = True,
                      frames_per_buffer = CHUNK)

print("TEST - Recording is starting")

input_audio_frames = [] # Will store the recorded audio data

def stop_recording():
    print("Stopping the recording...")
    global recording_flag
    recording_flag = False  # Terminate the recording

recording_flag = True

# Stop the recording when pressed enter

keyboard.on_press_key('enter', lambda _: stop_recording())

# Reading audio data
while recording_flag:
    audio_data = audio_stream.read(CHUNK)
    input_audio_frames.append(audio_data)

# Terminating the audio stream

audio_stream.stop_stream()
audio_stream.close()
p.terminate()

# Create and write the audio data into a WAV file

output_file = wave.open(TEMP_REC_FILENAME, "wb")

output_file.setnchannels(CHANNELS)
output_file.setsampwidth(p.get_sample_size(FORMAT))
output_file.setframerate(SAMPLE_RATE)

output_file.writeframes(b''.join(input_audio_frames))

output_file.close()

print(f"TEST - Recording file was saved to {TEMP_REC_FILENAME}")


