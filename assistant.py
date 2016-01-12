#!/usr/bin/env python

import apiai
import pyaudio
import time
import json
import pyttsx
import platform
import os
import icalendar

CLIENT_ACCESS_TOKEN = 'ae9ba44bfc784edfb047fa865c8e0a0c'
SUBSCRIPTION_KEY = 'bb578bf5-b17b-4a22-bf0d-4aa2492e0401' 

RATE = 44100
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RECORD_SECONDS = 2

def main():

    setupCampusEvents()

    while True:
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

        print platform.system()


        print("Wait for response...")
        response = request.getresponse()
        jsonString = (response.read()).decode('utf-8')
        processResponse(jsonString)
        

def processResponse(jsonString):
    jsonResponse = json.loads(jsonString)

    stringResponse = jsonResponse["result"]["fulfillment"]["speech"]
    stringResponse = stringResponse.rstrip()

    print(stringResponse)

    if stringResponse is not None and stringResponse != "":
        if platform.system() == 'Darwin':
            os.system("say " + '"' + stringResponse + '"')
        else:
            print 'Windows'

    else:
        print(jsonString)
        parameters = jsonResponse["result"]["parameters"]
        action = jsonResponse["result"]["action"]
        responseHelper(action, parameters)


def setupCampusEvents():
    calendar = open('cmu.ics','rb')
    gcal = icalendar.Calendar.from_ical(calendar.read())
    for component in gcal.walk():
        #if component.name == "VEVENT":
        print component.get('summary')
        #print component.get('dtstart')
        #print component.get('dtend')
        #print component.get('dtstamp')
    calendar.close()


#Processes advanced requests that cannot
#be handled on api.ai server
def responseHelper(action, parameters):
    speechText = ''
    if action == "get_free_food":
        speechText = "Build18 is currently giving out free Chipotle in Hamerschlag Hall."
        os.system("say " + '"' + speechText + '"')

    elif action == "get_events":
        nop
    elif action == "get_weather" or action == "weather.search":
        ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN, SUBSCRIPTION_KEY)
        request = ai.text_request()
        request.lang = 'en'
        
        if "date" in parameters:
            date = parameters["date"]
            date = date[:10]
            request.query = "What's the weather in Pittsburgh, PA on " + date;
        else: # Date was specified
            request.query = "What's the weather in Pittsburgh, PA"
        response = request.getresponse()
        jsonString = (response.read()).decode('utf-8')
        processResponse(jsonString)
    elif action == "get_directions" and "buildings" in parameters:
        building = parameters["buildings"]
        print "Parameter: " + building
        jsonData = open('directions.json').read()
        print jsonData
        buildingData = json.loads(jsonData)
        speechText = buildingData[building]
        print "Speech: " + speechText
        os.system("say " + '"' + speechText + '"')


if __name__ == '__main__':
	main()