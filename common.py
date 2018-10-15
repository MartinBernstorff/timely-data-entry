import time
import os
from datetime import datetime as dt

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome

#Import credentials
from credentials import email, password
from emoji import UNICODE_EMOJI

###########################
# Init browser and log in #
###########################
def init(index_str):
    global b
    options = Options()
    options.add_argument("--headless") # Runs Chrome in headless mode.
    options.add_argument('--no-sandbox') # # Bypass OS security model
    options.add_argument('--start-maximized')
    options.add_argument('disable-infobars')
    options.add_argument("--disable-extensions")

    b = webdriver.Chrome(chrome_options=options)
    b.get('https://app.timelyapp.com/836406/calendar/day?date={}'.format(index_str))

    b.maximize_window()

    print("Driver started")
    print("Logging in")
    # Login
    elem = b.find_element_by_id("user_email")
    elem.send_keys(email)

    elem = b.find_element_by_id("user_password")
    elem.send_keys(password)
    elem.send_keys(Keys.RETURN)
    print("Log-in succesful")

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
def fill_field(selector, value, delay=0.1):
    wait_for_element(selector)
    el = b.find_element_by_css_selector(selector)
    el.clear()
    time.sleep(delay)
    el.clear()
    print("     Entering '{}'".format(value))
    el.send_keys(value)
    time.sleep(delay)

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
        element = WebDriverWait(b, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
    finally:
        pass

def update_entry(entry, name, start_time, end_time):
    if contains_emoji(name) is True:
        print("{} contains emoji, skipping".format(name))
    else:
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

        time.sleep(0.3)
        entry.click()
        print("  Clicking {}".format(name))
        time.sleep(0.3)

        # Update time
        start_time_fmt = start_time.strftime("%H:%M")
        end_time_fmt = end_time.strftime("%H:%M")

        print("  Updating start- and endtimes")
        fill_field("input[name='from']", start_time_fmt, delay=0.8)
        fill_field("input[name='to']", end_time_fmt, delay=0.8)

        # Submit
        time.sleep(0.8)
        send_return("button.Button__success___3mVd2")
        print("{} processed".format(name))
        time.sleep(0.8)

def contains_emoji(s):
    count = 0
    for emoji in UNICODE_EMOJI:
        count += s.count(emoji)
    return bool(count)

def add_entry(name, start_time, end_time, project=None, tags=None, planned=True):
    '''
    Adds a new entry. Takes the following:
        Name: Entry name (str)
        Start_time: Entry start_time (Gcal format)
        End_time: See above
        Project: Entry project (str)
        Planned: Whether pre-planned (bool)
    '''
    if contains_emoji(name) is True:
        print("{} contains emoji, skipping".format(name))
    else:
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
        time.sleep(0.6)

        # Set entry start- and end-time
        click_element("span.fa-arrows-h")
        time.sleep(0.3)

        start_time_fmt = start_time.strftime("%H:%M")
        end_time_fmt = end_time.strftime("%H:%M")

        fill_field("input[name='from']", start_time_fmt, delay=0.8)
        fill_field("input[name='to']", end_time_fmt, delay=0.8)

        if name == "Sleep":
            fill_field("input[name='hours']", hours)
            fill_field("input[name='minutes']", minutes)

        fill_field("textarea#tag-input", name)

        # Set planned time
        if planned is not False:
            click_element("div[data-hint='Set planned time']")

            fill_field("input[name='estimated_hours']", hours, delay=0.3)
            fill_field("input[name='estimated_minutes']", minutes, delay=0.3)

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
            click_element(".TagDropdown__noTags___M2_Fp")
            for tag in tags:
                print("    Adding {} tag".format(tag))
                fill_field(".Input__container___32lm1", tag)
                fill_field(".Input__container___32lm1", tag) # Bug in Timely, re-fill
                send_return(".Input__container___32lm1")

        # Submit
        time.sleep(0.5)
        send_return("button.Button__success___3mVd2")
        time.sleep(0.5)
