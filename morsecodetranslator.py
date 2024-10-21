# audio_input
## only supports recording files for now
### only supports mono audio (CHANNEL = 1)
import numpy as np
import pyaudio
import wave
import keyboard
import librosa


def melspect_silence_error(normalized_audio_data, SAMPLE_RATE):
    # Process the normalized audio data with librosa
    mel_spect = librosa.feature.melspectrogram(y=normalized_audio_data, sr=SAMPLE_RATE)

    # Convert the mel spectrogram to dB
    mel_spect_db = librosa.power_to_db(mel_spect, ref=1.0)

    # Find the maximum dB value
    max_db = np.max(mel_spect_db)
    max_db = round(max_db, 2)
    if max_db < 2000:
            print("Silence Error: The recording is too quiet. Please record again.\n\n")
            global silence_error_flag
            silence_error_flag = True
            

def stop_recording():
        global recording_flag
        if recording_flag:        
            print("Stopping the recording...")
            recording_flag=False

def main():
    # User will decide these parameters through the GUI

    SAMPLE_RATE = int(input("Sample Rate (e.g 44100): "))

    # Static parameters

    FORMAT = pyaudio.paInt16 # Bit-depth ## paInt16 => 16-bit PCM (Pulse Code Modulation)
    CHANNELS = 1 # mono
    CHUNK = 1024 # Number of samples per each recording loop
    TEMP_REC_FILENAME = "temp_rec_mct.wav"

    global silence_error_flag
    silence_error_flag = False

    while 1:
        silence_error_flag = False
        p = pyaudio.PyAudio() # Initialize PortAudio

        # Starting the audio stream

        audio_stream = p.open(format = FORMAT,
                        channels = CHANNELS,
                        rate = SAMPLE_RATE,
                        input = True,
                        frames_per_buffer = CHUNK)

        print("TEST - Recording is starting")

        input_audio_frames = [] # Will store the recorded audio data

        global recording_flag
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

        # Convert the recorded data to numpy array
        audio_data = np.frombuffer(b''.join(input_audio_frames), dtype=np.int16)

        # Normalize the audio data using librosa
        normalized_audio_data = audio_data.astype(np.float32) / np.max(np.abs(audio_data))
        # Process the normalized audio data with librosa for the silence error
        melspect_silence_error(normalized_audio_data, SAMPLE_RATE)

        if (silence_error_flag == True):
             continue
        else:
             break


if __name__ == "__main__":
    main() # Run the main function

