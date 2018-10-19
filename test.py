import requests as r
import json
import datetime
from datetime import datetime as dt
import time

from task_dicts import task_project_pairs, event_exclude, task_tags

import gcal

base = "https://api.timelyapp.com/1.1/"

account_id = "836406"
client_id = "43a14e367ea2c0533aeef2867433008a4095f4b6e82e262123e34059f7535634"
client_secret = "06648768b93df35f26c3d9c77e72a5c5806b7eafddd4aeaabd25f65a217b31ba"
request_url = "https://api.timelyapp.com/1.1/oauth/authorize"
headers = {"Content-Type":"application/json","X-Accept":"application/json"}
redirect_uri = "http://google.com"
payload = {"response_type":"code","redirect_uri":redirect_uri,"client_id":client_id}

global refresh_token
global access_token

file = open("r_token.txt", "r")

current_refresh_token = file.read()
current_access_token = ""

def print_auth_url():
    url = "https://api.timelyapp.com/1.1/oauth/authorize?response_type=code&redirect_uri=" + redirect_uri + "&client_id=" + client_id
    print("Url: {}".format(url))

def get_auth_from_refresh(refresh_token):
    payload = {
        "redirect_uri": redirect_uri,
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }

    print("Getting new acces token via refresh token: {}".format(refresh_token))

    token_url = base + "/oauth/token"

    token_request = r.post(token_url,headers=headers,data=json.dumps(payload))
    global current_access_token
    current_access_token = token_request.json()['access_token']
    global current_refresh_token
    current_refresh_token = token_request.json()['refresh_token']
    file = open("refresh_token.txt", "w")
    file.write(current_refresh_token)

    print("Access token: {}".format(current_access_token))
    print("New refresh token: {}".format(current_refresh_token))

def get_something(extension):
    url = base + extension
    auth = "Bearer " + current_access_token
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth
    }

    print("Requesting \n   url: {}\n   headers: {}".format(url, headers))

    request = r.get(url, headers=headers)
    print(request)

    response = request.json()

    get_auth_from_refresh(current_refresh_token)

    return response

def strip_and_datetime(time_string):
    stripped = str(time_string)[:19]
    return dt.strptime(stripped, "%Y-%m-%dT%H:%M:%S")

def create_event(day, start_time, end_time, note=""):
    start_time_dt = strip_and_datetime(start_time)
    end_time_dt = strip_and_datetime(end_time)

    # Convert to unix
    start_time_ts = time.mktime(start_time_dt.timetuple())
    end_time_ts = time.mktime(end_time_dt.timetuple())

    # Calculate time in hours and minutes
    hours = int(end_time_ts-start_time_ts) // 3600
    minutes = int(end_time_ts-start_time_ts) // 60 % 60

    url = base + account_id + "/events"
    auth = "Bearer " + current_access_token
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth
    }

    payload = {
        "event": {
            "day": day,
            "from": start_time,
            "to": end_time,
            "hours": hours,
            "minutes": minutes,
            "estimated_hours": hours,
            "estimated_minutes": minutes,
            "note": note
        }
    }

    print("Sending \n   url: {}\n   headers: {}\n   payload: {}".format(url, headers, payload))

    request = r.post(url, headers=headers, data=json.dumps(payload))
    print(request)

    response = request.json()

    get_auth_from_refresh(current_refresh_token)
    return response

#Generate today-string
index = dt.today() + datetime.timedelta(1) #<--- Beware the time-delta!
index_midnight = index.replace(hour=0, minute=1)
index_formatted = index_midnight.isoformat() + 'Z'
index_str = dt.strftime(index,'%Y-%m-%d')

day_after_index = index + datetime.timedelta(1)
day_after_index_midnight = day_after_index.replace(hour=0, minute=1)
day_after_index_formatted = day_after_index_midnight.isoformat() + 'Z'

# Setup gcal
gcal.init(index_formatted, day_after_index_formatted)
from gcal import event_list
print(event_list)

get_auth_from_refresh(current_refresh_token)

day = "2018-10-19"

i = 0

NO_PROJECT_TXT = open("no_project.txt", "a")

for event in event_list: # Skip ith event, avoid sleep from day before
    if i == 0:
        i = i + 1
        print("Skipping event")
    elif i == 1:
        if event[0] in event_exclude:
            print("{} is an excluded event, not adding".format(event[0]))
        elif event[0] in task_project_pairs:
            pass
        else:
            NO_PROJECT_TXT.write(str(event[0]) + "\n")
    else:
        print("Exiting loop")
        break
