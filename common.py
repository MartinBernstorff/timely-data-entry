import time
from datetime import datetime as dt

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Firefox

#Import credentials
from credentials import email, password

###########################
# Init browser and log in #
###########################
def init(index_str):
    global b
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

def add_entry(name, start_time, end_time, project=None, tags=None, planned=True):
    '''
    Adds a new entry. Takes the following:
        Name: Entry name (str)
        Start_time: Entry start_time (Gcal format)
        End_time: See above
        Project: Entry project (str)
        Planned: Whether pre-planned (bool)
    '''
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

    # Add tags
    if tags is not None:
        print("Adding tags!")
        click_element(".TagDropdown__noTags___M2_Fp")
        for tag in tags:
            print("    Adding {}".format(tag))
            fill_field(".Input__container___32lm1", tag)
            fill_field(".Input__container___32lm1", tag) # Bug in Timely, re-fill
            send_return(".Input__container___32lm1")

    # Submit
    send_return("button.Button__success___3mVd2")
