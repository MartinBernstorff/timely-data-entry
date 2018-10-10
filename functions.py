# Other imports
from time import sleep
import time
import datetime
from datetime import datetime as dt
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

###########################
# Init browser and log in #
###########################
b = Firefox()
b.get('https://app.timelyapp.com/836406/calendar/day?date={}'.format(index_str))

# Login
elem = b.find_element_by_id("user_email")
elem.send_keys("martinbernstorff@gmail.com")

elem = b.find_element_by_id("user_password")
elem.send_keys("is8bames")
elem.send_keys(Keys.RETURN)

add_entry_selector = "EventAddButton__hover___11l17"

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
    el = b.find_element_by_css_selector(selector)
    el.clear()
    el.send_keys(value)

def get_field_value(selector):
    el = b.find_element_by_css_selector(selector)
    value = el.get_attribute("value")
    print(value)
    return value

def click_element(selector):
    el = b.find_element_by_css_selector(selector)
    el.click()

def send_return(selector):
    el = b.find_element_by_css_selector(selector)
    el.send_keys(Keys.RETURN)

def strip_and_datetime(time_string):
    stripped = str(time_string)[:19]
    return dt.strptime(stripped, "%Y-%m-%dT%H:%M:%S")

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
    sleep(1)

    # Update time
    start_time_fmt = start_time.strftime("%H:%M")
    end_time_fmt = end_time.strftime("%H:%M")

    if name == "Sleep":
        fill_field("input[name='hours']", hours)
        fill_field("input[name='minutes']", minutes)
    else:
        fill_field("input[name='from']", start_time_fmt)
        fill_field("input[name='to']", end_time_fmt)
        print("{} to {}".format(start_time_fmt, end_time_fmt))
    sleep(1)

    # Submit
    send_return("button.Button__success___3mVd2")

def add_entry(name, start_time, end_time, project):
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

    print("Adding {}".format(name))
    click_element(".{}".format(add_entry_selector))
    sleep(1)

    # Set entry start- and end-time
    click_element("span.fa-arrows-h")

    start_time_fmt = start_time.strftime("%H:%M")
    end_time_fmt = end_time.strftime("%H:%M")

    fill_field("input[name='from']", start_time_fmt)
    fill_field("input[name='to']", end_time_fmt)
    time.sleep(1)

    if name == "Sleep":
        fill_field("input[name='hours']", hours)
        fill_field("input[name='minutes']", minutes)

    fill_field("textarea#tag-input", name)

    # Set planned time
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
}
