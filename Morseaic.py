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
from intMorse import int_morse_table # Include morse code mapping dict

# ASCII ART GUI
file_name = "ascii_art.txt"

with open(file_name, "r") as file:
    content = file.read()
    print(content)

startcheckflag = False # Flag to start the program

def start_program(_):
    global startcheckflag
    keyboard.write('\b')
    startcheckflag = True
    
def clear_screen():
    # Clears the screen
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  
        os.system('clear')

keyboard.on_press_key('1', start_program) # If user presses 1,program starts 

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

def pattern_recognition(normalized_audio_data,SAMPLE_RATE, chunk_duration=0.01):

    # Calculate the number of samples per chunk
    chunk_samples = int(chunk_duration * SAMPLE_RATE)

    # Initialize the start and end indices for the chunks
    start_idx = 0
    pattern_counter = 0
    space_counter = 0

    global firstsignalflag
    firstsignalflag = False

    # Array to store the pattern of each chunk
    pattern_array = []

    # Loop through the audio signal in chunks
    while start_idx < len(normalized_audio_data):
        
        end_idx = min(start_idx + chunk_samples, len(normalized_audio_data))  # Ensure end_idx does not exceed the length of the audio data
        
        # Extract the current chunk
        chunk = normalized_audio_data[start_idx:end_idx]

        # Calculate the mean amplitude of the chunk
        mean_amplitude = np.mean(np.abs(chunk))

        # Convert mean amplitude to dB
        mean_amplitude_db = 20 * np.log10(mean_amplitude)
        mean_amplitude_db = round(mean_amplitude_db,2)
        

        if mean_amplitude_db > -20:
             pattern_counter += 1

             if space_counter > 10 and space_counter <= 50 and firstsignalflag == True:
                 pattern_array.append("type1")

             if space_counter > 50 and firstsignalflag == True:
                 pattern_array.append("type2")

             space_counter = 0

        elif mean_amplitude_db <= -20:
             space_counter += 1

             if pattern_counter > 10 and pattern_counter <= 55:
                 pattern_array.append('.')
                 firstsignalflag = True

             elif pattern_counter > 50:
                 firstsignalflag = True 
                 pattern_array.append('-')
             
             pattern_counter = 0

        # Update the start index for the next chunk
        start_idx += chunk_samples

    return pattern_array

def pattern_transformer(pattern_array, int_morse_table):
    temp_element_list = []
    temp_letter_list = []
    output_string = []

    for i in range(len(pattern_array)):
        element = pattern_array[i]

        if element == "type2":
            temp_letter_list.append("".join(temp_element_list))

            output_string.append(int_morse_table["".join(temp_letter_list)])
            output_string.append(" ")
            
            temp_element_list.clear()
            temp_letter_list.clear()

        elif element != "type1" and element != "type2":
            temp_element_list.append(element)


    translated_string = "".join(output_string)

    return translated_string

def main():
    global normalized_audio_data, SAMPLE_RATE
    # Fetch info about default input device (mic)
    default_sample_rate, default_channels = fetch_mic_info()

    
    print("===================================================================")
    print(f"default sample rate: {int(default_sample_rate)}")
    print(f"default channel number: {default_channels}")
    print("===================================================================\n\n")
    
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
        
    # Pattern recognition process
    pattern_array = pattern_recognition(normalized_audio_data, SAMPLE_RATE) 
    
    # TEST LINES DEL WHEN DONE
    print(pattern_array) #print the pattern array
    # TEST LINES END

    translated_string = pattern_transformer(pattern_array, int_morse_table)
    print(translated_string)
    
if __name__ == "__main__":
    main() # Run the main function

