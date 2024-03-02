from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import time
import speech_recognition as sr
import pyttsx3
import pytz
import subprocess

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "octomber", "november", "december"]
DAY_EXTENSIONS = ["st", "nd", "rd", "th"]

user = "Robert"

def speak(text):
    engine = pyttsx3.init()

    # voices = engine.getProperty('voices')

    # engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 155)
    engine.say(text)
    engine.runAndWait()

def get_audio_no_awake():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
        except:
            pass
    
    return said.lower()

def get_audio_awake():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            speak("I didn't quite understand that!")
            print("Exception: " + str(e))
    
    return said.lower()

def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            filename = r"C:\Users\User\Desktop\Workspaces\Python\Voice Assistant\credentials.json"
            flow = InstalledAppFlow.from_client_secrets_file(
                filename, SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service

def get_events(day, service):

    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.utc
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax = end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()

    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day.")

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start_time = str(start.split("T")[1].split("+")[0]) 
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "am"
            else: 
                start_time = str(int(start_time.split(":")[0]) - 12) + start_time.split(":")[1]
                start_time = start_time + "pm"

            speak(event["summary"] + " at " + start_time)

def get_date(text):
    if text == "":
        return

    today = datetime.date.today()

    if text.count("today") > 0:
        return today
    
    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
             for ext in DAY_EXTENSIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    if month < today.month and month != -1 or month == today.month and day < today.day and day != -1:
        year += 1
        
    if day < today.day and month == -1 and day != -1:
        month += 1
        
    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7
        return today + datetime.timedelta(dif)
        
    try:
        return datetime.date(month = month, day = day, year = year)
    except:
        # speak("You haven't picked any date")
        return None

def note(text):
    date = datetime.datetime.now()

    file_name = str(date).replace(":", "-") + "-note.txt"
    with open(file_name, "w") as f:
        f.write(text)

    subprocess.Popen(["notepad.exe", file_name])

WAKE = 'hey voice assistant'
service = authenticate_google()
print("Start")

while True:
    text = get_audio_no_awake()

    if text.count(WAKE) > 0:
        speak("Hello " + user + "!")
        text = get_audio_awake()

        # CHECK FUTURE EVENTS USING GOOGLE CALENDAR

        CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy", "what events do i have", "what is on"]
        for phrase in CALENDAR_STRS:
            if phrase in text:
                date = get_date(text)
                if date:
                    get_events(get_date(text), service)
                else:
                    speak("I don't understand")

        # MAKE A NOTE

        NOTE_STRS = ["make a note", "write something down", "remember this", "write for me", "write this down"]
        for phrase in NOTE_STRS:
            if phrase in text:
                speak("What would you like me to write down?")
                note_text = get_audio_awake()
                note(note_text)
                speak("I've made a note")


        # OPEN A NEW INTERNET TAB

        # OPEN YOUTUBE + PLAY SOME SONG/ARTIST

        # OPEN SPOTIFY + PLAY A PLAYLIST

        # OPEN VSCODE FILE

        # TRY: WIKIPEDIA, EXCEPT: GOOGLE SOMETHING