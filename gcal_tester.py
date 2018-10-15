import time
import datetime
from datetime import datetime as dt
import gcal
from common import *

index = dt.today() + datetime.timedelta(1) #<--- Beware the time-delta!
index_midnight = index.replace(hour=0, minute=1)
index_formatted = index_midnight.isoformat() + 'Z'
index_str = dt.strftime(index,'%Y-%m-%d')

day_after_index = index + datetime.timedelta(1)
day_after_index_midnight = day_after_index.replace(hour=0, minute=1)
day_after_index_formatted = day_after_index_midnight.isoformat() + 'Z'

gcal.init(index_formatted, day_after_index_formatted)
from gcal import event_list

def add_entry_tester(name, start_time, end_time):
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
        print("Adding {}".format(name))

        start_time_fmt = start_time.strftime("%H:%M")
        print(start_time_fmt)
        end_time_fmt = end_time.strftime("%H:%M")
        print(end_time_fmt)

for event in event_list:
    add_entry_tester(name=event[0], start_time=event[1], end_time=event[2])
