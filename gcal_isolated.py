# Other imports
from time import sleep
import time
import datetime
from datetime import datetime as dt
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

#Generate tomorrow-string
index = dt.today() + datetime.timedelta(3) #<--- Beware the time-delta!
index_midnight = index.replace(hour=0, minute=1)
index_formatted = index_midnight.isoformat() + 'Z'
index_str = dt.strftime(index,'%Y-%m-%d')

day_after_index = index + datetime.timedelta(1)
day_after_index_midnight = day_after_index.replace(hour=0, minute=1)
day_after_index_formatted = day_after_index_midnight.isoformat() + 'Z'

########################
# Baseline established #
########################
# Get calendar events
# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

event_list=[]

"""Shows basic usage of the Google Calendar API.
Prints the start and name of the next 10 events on the user's calendar.
"""
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))

# Call the Calendar API

# Get all calendars
calendar_list = service.calendarList().list().execute()

for calendar_list_entry in calendar_list['items']:
    print("{}".format(calendar_list_entry["summary"].encode("utf-8")))
