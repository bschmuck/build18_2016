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
import random
import cv2
import sys
from multiprocessing import Process, Manager


CLIENT_ACCESS_TOKEN = 'ae9ba44bfc784edfb047fa865c8e0a0c'
SUBSCRIPTION_KEY = 'bb578bf5-b17b-4a22-bf0d-4aa2492e0401'

# Twitter user credentials
ACCESS_TOKEN = '4797914969-ZNshVvSYGfhuBfdBNfKRlgVJOxjRi0XOaH6VQXu'
ACCESS_SECRET = 'MsB3MahVJR5bVgZP96SpbRYiXCX0HO2jp9vivIJ6r5Vpk'
CONSUMER_KEY = 'JK8l3Vfa2gljT7sTcyg3586iy'
CONSUMER_SECRET = 'DQhmMv4FF6PHcJayZaLkbUzxRBMvzQ33y4Mm3t2PFWYiIMdbgK'

#Audio recording settings
RATE = 44100
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RECORD_SECONDS = 2

#Set up Twitter posting
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

#Boolean to determine whether voice assistant is talking
isTalking = False

#Dictionary of hour information for campus restaurants
campusFoodHours = {}

#Parses open and close times for campus restaurants
def parseCampusFoodInfo():
    jsonData = open('campus_food_info.json').read()
    restaurantData = json.loads(jsonData)
    locationArray = restaurantData["locations"]
    for location in locationArray:
        locationName = location["name"]
        locationTimes = location["times"]
        campusFoodHours[locationName] = locationTimes

#Outputs text to speech and updates Twitter status
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

#Uses key commands to manage face
#movements in background

def doRandom():
    letters = ['Z','Y','W','N']
    ind = random.randint(0, 3)
    return letters[ind]

def faceTracker():
    print "Face Track running"
    k = PyKeyboard()
    
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    video_capture = cv2.VideoCapture(0)
    centerX = 0;

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(150, 150),    )
        
        #Draw a rectangle around the face
        if len(faces) >= 1:
            (x,y,w,h) = faces[0]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            centerNew = x + w/2
        if centerNew > centerX + 10:
            print('left')
            k.tap_key('Left')
        if centerNew < centerX - 10:
            print('right')
            k.tap_key('Right')
        centerX = centerNew
    
        if cv2.waitKey(1) & 0xFF == ord('q'):
               break

    # When everything is done, release the capture
    video_capture.release()
    cv2.destroyAllWindows()

def faceManager(threadName, delay):
    global isTalking

    k = PyKeyboard()
    isPressing = False

    #Presses and holds 'B' key to move mouth
    while True:
        for waitInd in range(235):
            if waitInd == 2 and not isTalking:
                # Do random action
                newKey = doRandom()
                k.press_key(newKey)
                time.sleep(.1)
                k.release_key(newKey)
                k.press_key(newKey)
                time.sleep(.1)
                k.release_key(newKey)
                time.sleep(3)
                # start blinking again
                k.press_key('K')
                time.sleep(.1)
                k.release_key('K')
            if isTalking:
                if not isPressing:
                    k.press_key('B')
                isPressing = True
            else:
                if isPressing:
                    k.release_key('B')
                    isPressing = False
                    # start blinking again
                    k.press_key('K')
                    time.sleep(.1)
                    k.release_key('K')
            time.sleep(.1)



#Main functio
def main():
    global isTalking

    #Parses information from files for information
    setupCampusEvents()
    parseCampusFoodInfo()

    
    
    
    try:
        thread.start_new_thread(faceManager, ("Thread-1", 2, ) )
        #thread.start_new_thread(faceTracker,  )
        #faceTracker()
        
    except:
        print "Could not start Thread"

    while True:
       
        resampler = apiai.Resampler(source_samplerate = RATE)
        vad = apiai.VAD()
        ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN, SUBSCRIPTION_KEY)

        r = sr.Recognizer()
        speechText = ""

        #use the default microphone as the audio source
        with sr.Microphone() as source:
            #filter ambient noise               
            r.adjust_for_ambient_noise(source)        
            print "Ready!"

            #Listens for user input
            try:
                audio = r.listen(source)
            except:
                print "Try again"

        #Google Speech to Text
        try:
            speechText = r.recognize_google(audio)
            print("You said " + speechText)    
        except LookupError:                          
            print("Could not understand audio")
            continue
        except sr.UnknownValueError:
            print("Unintelligible speech.")
            continue

        #Sends text request to API.ai
        request = ai.text_request()
        request.lang = 'en'
        request.query = speechText

        #Waits for response from server and processes
        print("Wait for response...")
        response = request.getresponse()
        jsonString = (response.read()).decode('utf-8')
        processResponse(jsonString)
    
    

#Processes the response from API.ai
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

        endMinString = ''
        nextStartMinString = ''

        if endMin == 0:
            endMinString = "O Clock"
        else:
            endMinString = str(endMin)

        if nextStartMin == 0:
            nextStartMinString = "O Clock"
        else:
            nextStartMinString = str(nextStartMin)

        if (int(day) < int(endDay)) or (int(currentHour) < int(endHour) and int(day) == int(endDay)) or (int(day) == int(endDay) and int(currentHour) == int(endHour) and int(currentMin) < int(endMin)):
            speechText = restaurantName + " is currently open. It will remain open until " + str(endHour) + " " + endMinString
        else:
            print "Days Equal: " + str((currentDay == endDay)) + "Hours LT: " + str((currentHour < endHour))
            speechText = restaurantName + " is currently closed. It will reopen at " + str(nextStartHour) + "b " + nextStartMinString

        processTextToVoice(speechText)

    elif action == "get_open_restaurants":
        day = datetime.datetime.today().weekday()
        openRestaurants = []
        for restaurant in campusFoodHours:
            restaurantTimes = campusFoodHours[restaurant]
            didFindHours = False
            for time in restaurantTimes:
                if not didFindHours:
                    if time["start"]["day"] == day and not didFindHours:
                        startHour = time["start"]["hour"]
                        startMin = time["start"]["min"]
                        endHour = time["end"]["hour"]
                        endMin = time["end"]["min"]
                        endDay = time["end"]["day"]
                        didFindHours = True
                elif didFindHours:
                    nextStartHour = time["start"]["hour"]
                    nextStartMin = time["start"]["min"]
                    break

            now = datetime.datetime.now()
            currentHour = now.hour
            currentMin = now.minute

            if (int(day) < int(endDay)) or (int(currentHour) < int(endHour) and int(day) == int(endDay)) or (int(day) == int(endDay) and int(currentHour) == int(endHour) and int(currentMin) < int(endMin)):
                openRestaurants.append(restaurant)

        openRestaurantsText = "The following restaurants are currently open: "
        print openRestaurants
        for openRestaurant in openRestaurants:
            print "Open " + openRestaurant
            openRestaurantsText = openRestaurantsText + " " + openRestaurant.encode('utf-8')
        processTextToVoice(openRestaurantsText)

    else:
        processTextToVoice("Sorry, I did not understand.")


if __name__ == '__main__':
	main()
