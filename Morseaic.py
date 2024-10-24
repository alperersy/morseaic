# morsecodetranslator.py
## only supports recording files for now

# alperersy, yefesaktas

import numpy as np
import pyaudio
import wave
import keyboard
import librosa
import time
import os
#ASCII ART GUI
file_name = "ascii_art.txt"
with open(file_name, "r") as file:
    content = file.read()
    print(content)
startcheckflag = False #flag to start the program
def start_program(_):
    global startcheckflag
    keyboard.write('\b')
    startcheckflag = True
    
def clear_screen():
    #clears the screen
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  
        os.system('clear')

keyboard.on_press_key('1', start_program) #if user presses 1,program starts 

while not startcheckflag:
    time.sleep(0.1)
clear_screen()

def fetch_mic_info(): 
    # Fetch info about default input device (mic)
    p = pyaudio.PyAudio()
    default_input_device_info = p.get_default_input_device_info()

    # Default sample rate
    default_sample_rate = default_input_device_info["defaultSampleRate"]

    # Default channel number
    default_channels = default_input_device_info["maxInputChannels"]

    return default_sample_rate, default_channels

def melspect_silence_error(normalized_audio_data, SAMPLE_RATE):
    # Process the normalized audio data with librosa
    mel_spect = librosa.feature.melspectrogram(y=normalized_audio_data, sr=SAMPLE_RATE)

    # Convert the mel spectrogram to dB
    mel_spect_db = librosa.power_to_db(mel_spect, ref=1.0)

    # Find the maximum dB value
    max_db = np.max(mel_spect_db)
    max_db = round(max_db, 2)
    if max_db < 20:
            print("*******************************************************************")
            print("Silence Error: The recording is too quiet. Recording has restarted\n")
            print("*******************************************************************\n\n")
            global silence_error_flag
            silence_error_flag = True
            

def stop_recording():
        global recording_flag
        if recording_flag:        
            print("****** Stopping the recording... ******\n\n")
            recording_flag=False

def main():
    # Fetch info about default input device (mic)
    default_sample_rate, default_channels = fetch_mic_info()

    # TEST
    print("===================================================================")
    print(f"default sample rate: {int(default_sample_rate)}")
    print(f"default channel number: {default_channels}")
    print("===================================================================\n\n")
    
    # TEST END

    

    SAMPLE_RATE = int(default_sample_rate)
    FORMAT = pyaudio.paInt16 # Bit-depth ## paInt16 => 16-bit PCM (Pulse Code Modulation)
    CHANNELS = default_channels
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
        print("------------------------------------------------------------------------------")
        print("--------- Recording has started. Press 'ENTER' to stop the recording ---------\n",end="")
        print("------------------------------------------------------------------------------\n\n")
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

        print(f"Recording file successfully saved to '{TEMP_REC_FILENAME}'!\n\n")

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

