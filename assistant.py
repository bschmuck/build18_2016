#!/usr/bin/env python

import apiai
import pyaudio
import time
import json
import pyttsx
import os

CLIENT_ACCESS_TOKEN = 'ae9ba44bfc784edfb047fa865c8e0a0c'
SUBSCRIPTION_KEY = 'bb578bf5-b17b-4a22-bf0d-4aa2492e0401' 

RATE = 44100
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RECORD_SECONDS = 2

def onFinishUtterance(name, isCompleted):
    print("Finished!")

def main():
    engine = pyttsx.init()
    engine.setProperty('rate', 200)
    voices = engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')


    resampler = apiai.Resampler(source_samplerate = RATE)
    vad = apiai.VAD()
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN, SUBSCRIPTION_KEY)
    request = ai.voice_request()
    request.lang = 'en'

    def streamCallback(in_data, frame_count, time_info, status):
        frames, data = resampler.resample(in_data, frame_count)
        state = vad.processFrame(frames)
        request.send(data)

        if(state == 1):
            return in_data, pyaudio.paContinue
        else:
            return in_data, pyaudio.paComplete

    pyAud = pyaudio.PyAudio()

    stream = pyAud.open(format = FORMAT,
                        channels = CHANNELS,
                        rate = RATE,
                        input = True,
                        output = False,
                        frames_per_buffer = CHUNK,
                        stream_callback = streamCallback
                        )

    stream.start_stream()

    print("Yo man. Say something!")

    try:
        while stream.is_active():
            time.sleep(0.1)
    except Exception:
        raise e
    except KeyboardInterrupt:
        pass

    stream.stop_stream()
    stream.close()
    pyAud.terminate()


    print("Wait for response...")
    response = request.getresponse()

    jsonString = (response.read()).decode('utf-8')
    jsonResponse = json.loads(jsonString)

    stringResponse = jsonResponse["result"]["fulfillment"]["speech"]
    stringResponse = stringResponse.rstrip()

    if stringResponse is not None and stringResponse != "":
        print(stringResponse)
        engine.say(stringResponse)
        engine.runAndWait()

    main()

if __name__ == '__main__':
	main()