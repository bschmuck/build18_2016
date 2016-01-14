#!/usr/bin/env python

import apiai
import pyaudio
import time
import json
import pyttsx
import platform
import os
import icalendar
import tweepy
import thread
from pykeyboard import PyKeyboard
import time
import datetime
import speech_recognition as sr


CLIENT_ACCESS_TOKEN = 'ae9ba44bfc784edfb047fa865c8e0a0c'
SUBSCRIPTION_KEY = 'bb578bf5-b17b-4a22-bf0d-4aa2492e0401'

# Twitter user credentials
ACCESS_TOKEN = '4797914969-ZNshVvSYGfhuBfdBNfKRlgVJOxjRi0XOaH6VQXu'
ACCESS_SECRET = 'MsB3MahVJR5bVgZP96SpbRYiXCX0HO2jp9vivIJ6r5Vpk'
CONSUMER_KEY = 'JK8l3Vfa2gljT7sTcyg3586iy'
CONSUMER_SECRET = 'DQhmMv4FF6PHcJayZaLkbUzxRBMvzQ33y4Mm3t2PFWYiIMdbgK'

RATE = 44100
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RECORD_SECONDS = 2

#Set up Twitter posting
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

isTalking = False

campusFoodHours = {}



def parseCampusFoodInfo():
    jsonData = open('campus_food_info.json').read()
    restaurantData = json.loads(jsonData)
    locationArray = restaurantData["locations"]
    for location in locationArray:
        locationName = location["name"]
        locationTimes = location["times"]
        campusFoodHours[locationName] = locationTimes

def processTextToVoice(text):
    global isTalking

    isTalking = True
    os.system("say -v Samantha " + '"' + text + '"')
    isTalking = False

    status = "Tank: " + text

    status = status[:139]
    try:
        api.update_status(status=status)
    except:
        print "Duplicate Tweet"


def faceManager(threadName, delay):
    k = PyKeyboard()

    global isTalking
    isPressing = False

    while True:
        if isTalking:
            if not isPressing:
                k.press_key('B')
            isPressing = True
        else:
            if isPressing:
                k.release_key('B')
            isPressing = False
        time.sleep(.1)


def main():

    global isTalking

    setupCampusEvents()
    parseCampusFoodInfo()

    try:
        thread.start_new_thread(faceManager, ("Thread-1", 2, ) )
    except:
        print "Could not start Thread"

    while True:

        resampler = apiai.Resampler(source_samplerate = RATE)
        vad = apiai.VAD()
        ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN, SUBSCRIPTION_KEY)


        r = sr.Recognizer()
        speechText = ""

        with sr.Microphone() as source:                # use the default microphone as the audio source
            r.adjust_for_ambient_noise(source)         # listen for 1 second to calibrate the energy threshold for ambient noise levels
            print "Ready!"

            try:
                audio = r.listen(source)
                print "Checkpoint"
            except:
                print "Try again"

        try:
            speechText = r.recognize_google(audio)
            print("You said " + speechText)    # recognize speech using Google Speech Recognition
        except LookupError:                            # speech is unintelligible
            print("Could not understand audio")
            continue
        except sr.UnknownValueError:
            print("Unintelligible speech.")
            continue
        #request = ai.voice_request()

        request = ai.text_request()
        request.lang = 'en'
        request.query = speechText

        print("Wait for response...")
        response = request.getresponse()
        jsonString = (response.read()).decode('utf-8')
        processResponse(jsonString)


def processResponse(jsonString):
    global isTalking

    jsonResponse = json.loads(jsonString)

    userRequest = jsonResponse["result"]["resolvedQuery"]
    status = "Client: " + userRequest
    status = status[:139]

    try:
        api.update_status(status=status)
    except:
        print "Duplicate Tweet"

    stringResponse = jsonResponse["result"]["fulfillment"]["speech"]
    stringResponse = stringResponse.rstrip()

    print(stringResponse)

    if stringResponse is not None and stringResponse != "":
        if platform.system() == 'Darwin':
            processTextToVoice(stringResponse)

        else:
            print 'Windows'

    else:
        print(jsonString)

        action = ""
        parameters = ""
        if "result" in jsonResponse:
            result = jsonResponse["result"]
            if "parameters" in result:
                parameters = result["parameters"]
            if "action" in result:
                action = result["action"]
        responseHelper(action, parameters)


def setupCampusEvents():
    global isTalking

    calendar = open('cmu.ics','rb')
    gcal = icalendar.Calendar.from_ical(calendar.read())
    for component in gcal.walk():
        print component.get('summary')
    calendar.close()


#Processes advanced requests that cannot
#be handled on api.ai server
def responseHelper(action, parameters):
    global isTalking
    global campusFoodHours

    speechText = ''
    if action == "get_free_food":
        speechText = "Build18 is currently giving out free Chipotle in Hamerschlag Hall."
        processTextToVoice(speechText)

    elif action == "get_events":
        print "Not implemented"
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
        processTextToVoice(speechText)

    elif action == "get_restaurant_status" and "restaurants" in parameters:
        day = datetime.datetime.today().weekday()
        restaurantName = parameters["restaurants"]
        restaurantTimes = campusFoodHours[restaurantName]

        print restaurantTimes

        startHour = 0
        startMin = 0
        startDay = day

        endHour = 0
        endMin = 0
        endDay = 0

        nextStartHour = 0
        nextStartMin = 0

        didFindHours = False;

        speechText = ""

        for time in restaurantTimes:
            if not didFindHours:
                print "Time: " + str(time["start"]["day"]) + " Looking for: " + str(day)
                if time["start"]["day"] == day and not didFindHours:
                    startHour = time["start"]["hour"]
                    startMin = time["start"]["min"]
                    endHour = time["end"]["hour"]
                    endMin = time["end"]["min"]
                    endDay = time["end"]["day"]
                    didFindHours = True
                    print "Found Time"
                elif didFindHours:
                    nextStartHour = time["start"]["hour"]
                    nextStartMin = time["start"]["min"]
                    break

        now = datetime.datetime.now()
        currentHour = now.hour
        currentMin = now.minute

        print "Current Time: " + str(currentHour) + ":" + str(currentMin) + " Date:" + str(startDay)
        print "End Time: " + str(endHour) + ":" + str(endMin) + " Date:" + str(endDay)

        if (int(day) < int(endDay)) or (int(currentHour) < int(endHour) and int(day) == int(endDay)) or (int(day) == int(endDay) and int(currentHour) == int(endHour) and int(currentMin) < int(endMin)):
            speechText = restaurantName + " is currently open. It will remain open until " + str(endHour) + ":" + str(endMin)
        else:
            print "Days Equal: " + str((currentDay == endDay)) + "Hours LT: " + str((currentHour < endHour))
            speechText = restaurantName + " is currently closed. It will reopen at " + str(nextStartHour) + ":" + str(nextStartMin)

        processTextToVoice(speechText)

    elif action == "get_open_restaurants":
        # BRANDON ADD YOUR CODE HERE
    else:
        processTextToVoice("Sorry, I did not understand.")


if __name__ == '__main__':
	main()
