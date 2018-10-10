# Selenium imports
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys

# Other imports
from time import sleep
import time
import datetime
from datetime import datetime as dt
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

#Import credentials
from credentials import email, password

#Generate tomorrow-string
index = dt.today() + datetime.timedelta(int(sys.argv[1])) #<--- Beware the time-delta!
index_midnight = index.replace(hour=0, minute=1)
index_formatted = index_midnight.isoformat() + 'Z'
index_str = dt.strftime(index,'%Y-%m-%d')

day_after_index = index + datetime.timedelta(1)
day_after_index_midnight = day_after_index.replace(hour=0, minute=1)
day_after_index_formatted = day_after_index_midnight.isoformat() + 'Z'

###########################
# Init browser and log in #
###########################
b = Firefox()
b.get('https://app.timelyapp.com/836406/calendar/day?date={}'.format(index_str))

# Login
elem = b.find_element_by_id("user_email")
elem.send_keys(email)

elem = b.find_element_by_id("user_password")
elem.send_keys(password)
elem.send_keys(Keys.RETURN)

# Wait for page loaded
try:
    element = WebDriverWait(b, 90).until(
        EC.presence_of_element_located((By.CLASS_NAME, "WorkHistoryEntry__timelineIcon___18ugC"))
    )
finally:
    print("Page loaded!")

####################
# Helper functions #
####################
def fill_field(selector, value):
    wait_for_element(selector)
    el = b.find_element_by_css_selector(selector)
    el.clear()
    el.send_keys(value)

def get_field_value(selector):
    wait_for_element(selector)
    el = b.find_element_by_css_selector(selector)
    value = el.get_attribute("value")
    print(value)
    return value

def click_element(selector):
    wait_for_element(selector)
    el = b.find_element_by_css_selector(selector)
    el.click()

def send_return(selector):
    wait_for_element(selector)
    el = b.find_element_by_css_selector(selector)
    el.send_keys(Keys.RETURN)

def strip_and_datetime(time_string):
    stripped = str(time_string)[:19]
    return dt.strptime(stripped, "%Y-%m-%dT%H:%M:%S")

def wait_for_element(selector):
    try:
        element = WebDriverWait(b, 90).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
    finally:
        pass

def update_entry(entry, name, start_time, end_time):
    start_time = strip_and_datetime(start_time)
    end_time = strip_and_datetime(end_time)

    # Convert to unix
    start_time_ts = time.mktime(start_time.timetuple())
    end_time_ts = time.mktime(end_time.timetuple())

    # Calculate time in hours and minutes
    hours = int(end_time_ts-start_time_ts) // 3600
    minutes = int(end_time_ts-start_time_ts) // 60 % 60

    # Create formatted start_time
    start_time_fmt = start_time.strftime("%H:%M")

    ############
    # Starting #
    ############

    # Open element
    print("Updating {}".format(name))
    entry.click()

    # Update time
    start_time_fmt = start_time.strftime("%H:%M")
    end_time_fmt = end_time.strftime("%H:%M")

    if name == "Sleep":
        fill_field("input[name='from']", start_time_fmt)
        fill_field("input[name='hours']", hours)
        fill_field("input[name='minutes']", minutes)
    else:
        fill_field("input[name='from']", start_time_fmt)
        fill_field("input[name='to']", end_time_fmt)
        print("{} to {}".format(start_time_fmt, end_time_fmt))

    # Submit
    send_return("button.Button__success___3mVd2")

def add_entry(name, start_time, end_time, project, planned=True):
    start_time = strip_and_datetime(start_time)
    end_time = strip_and_datetime(end_time)

    # Convert to unix
    start_time_ts = time.mktime(start_time.timetuple())
    end_time_ts = time.mktime(end_time.timetuple())

    # Calculate time in hours and minutes
    hours = int(end_time_ts-start_time_ts) // 3600
    minutes = int(end_time_ts-start_time_ts) // 60 % 60

    ############
    # Starting #
    ############

    add_entry_selector = "EventAddButton__container___1rzOq"

    print("Adding {}".format(name))
    click_element(".{}".format(add_entry_selector))

    # Set entry start- and end-time
    click_element("span.fa-arrows-h")

    start_time_fmt = start_time.strftime("%H:%M")
    end_time_fmt = end_time.strftime("%H:%M")

    fill_field("input[name='from']", start_time_fmt)
    fill_field("input[name='to']", end_time_fmt)

    if name == "Sleep":
        fill_field("input[name='hours']", hours)
        fill_field("input[name='minutes']", minutes)

    fill_field("textarea#tag-input", name)

    # Set planned time
    if planned is not False:
        click_element("div[data-hint='Set planned time']")

        fill_field("input[name='estimated_hours']", hours)
        fill_field("input[name='estimated_minutes']", minutes)

    # Set project
    if project is not None:
        el = b.find_element_by_css_selector("div.Select-value-label")
        el.click()
        el = b.find_element_by_css_selector("input[role='combobox']")
        el.send_keys(project)
        el.send_keys(Keys.RETURN)
    else:
        el = b.find_element_by_css_selector("div.Select-value-label")
        el.click()
        el = b.find_element_by_css_selector("input[role='combobox']")
        el.send_keys("Uncategorized")
        el.send_keys(Keys.RETURN)

    # Submit
    send_return("button.Button__success___3mVd2")
    time.sleep(1)

task_project_pairs = {
    "Wake up + shower": "Morn",
    "Meditate + breakfast": "Morn",
    "Undervisermøde": "Epi",
    "Morgen-konf.": "Psychiatry-clinic",
    "Mid-day meditation": "Rest",
    "Købe ind": "Food",
    "Dinner": "Food",
    "Lunch": "Food",
    "Review & plan": "Daily review",
    "Træne": "Workout",
    "Weekly planning": "Weekly review",
    "Day One: Weekly meditation": "Weekly review",
    "Forberede mig til næste epi-undervisning": "Epi",
    "Sleep": "Sleep",
    "M ❤️'": "Mieke",
    "Game 💪": "Mads",
    "Afdelingsarbejde": "Psychiatry-clinic",
    "Misc. routine": "Misc. routine",
    "Pakke ud": "Miscel",
    "Anki #All": "Pensum",
    "Undervisning": "Psychiatry-clinic",
    "Shave": "Mainten",
    "Far og Martin – Snak": "Famil",
    "Mor og Martin – Snak": "Famil",
    "Empty out inbox": "Empty out inbox",
    "Journal Club": "Psychiatry-clinic",
    "Middags-konf": "Psychiatry-clinic"
}

event_exclude = {
    "🌛",
    "Transport",
    "M ❤️"
    "Sleep"
}

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

# Get all calendars
calendar_list = service.calendarList().list().execute()

for calendar_list_entry in calendar_list['items']:
    if calendar_list_entry["summary"] == "E18_04semHold15":
        continue
    else:
        events_result = service.events().list(calendarId=calendar_list_entry["id"],
                                              timeMin=index_formatted,
                                              timeMax=day_after_index_formatted,
                                              singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        for event in events:
            if "dateTime" in event['start'] and "dateTime" in event['end']:
                event_list.append([event['summary'],
                                   event['start']['dateTime'],
                                   event['end']['dateTime']
                                   ])

event_list.sort(key=lambda x: x[1])

#####################
# Update old events #
#####################

entries = b.find_elements_by_css_selector("div.Event__container___3Iatm")

print("Original event_list")
print(event_list)

for entry in entries:
    title_css = "div.Event__eventContent___2P8C3 div.Event__contentClipper___2mL46 span.Event__header___13d1z span span"
    title = entry.find_element_by_css_selector(title_css).text
    matched = 0 #Whether the entry has matched an event

    for event in event_list:
        if event[0] in event_exclude:
            print("{} excluded".format(event[0]))
            matched = 1
            event_list.pop(event_list.index(event))
            break
        elif event[0] == title:
            print("Match found for {}, adding".format(title))
            update_entry(entry=entry, name=title, start_time=event[1],
                         end_time=event[2])
            event_list.pop(event_list.index(event))
            print("New event_list")
            print(event_list)
            matched = 1
            break

    if matched == 0:
        print("{} not in event_list, setting time = 0".format(title))
        update_entry(entry=entry, name=title, start_time=event[1],
                 end_time=event[1])

####################
# Enter new events #
####################
i = 1 # Skipping first Sleep event

if i == 1:
    i = i+1
    continue
else:
    print("{} not found in entry-list, adding".format(event_list))

    for event in event_list: # Skip ith event, avoid sleep from day before
        if event[0] in task_project_pairs:
            add_entry(name=event[0], start_time=event[1], end_time=event[2],
                        project=task_project_pairs[event[0]], planned=False)
        elif event[0] in event_exclude:
            print("{} is an excluded event, not adding".format(event[0]))
        else:
            add_entry(name=event[0], start_time=event[1], end_time=event[2],
                        project=None, planned=False)

b.quit()
