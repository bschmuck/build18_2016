#! /usr/bin/env bash

sudo pip install --upgrade pip
sudo pip install apiai
# portaudio is C module necessary for pyaudio (Clang fails if it's missing)
sudo brew install portaudio
sudo pip install pyaudio
sudo pip install pyttsx
sudo pip install icalendar
sudo pip install tweepy
sudo pip install pyuserinput
sudo pip install pyobjc-framework-Quartz
sudo brew install flac
sudo pip install SpeechRecognition
