# Selenium imports
import sys

# Other imports
from time import sleep
import time
import datetime
from datetime import datetime as dt

# Get task_dicts
from task_dicts import task_project_pairs, event_exclude, task_tags

# Import helper functions
from common import *
import gcal

#Generate tomorrow-string
index = dt.today() + datetime.timedelta(int(sys.argv[1])) #<--- Beware the time-delta!
index_midnight = index.replace(hour=0, minute=1)
index_formatted = index_midnight.isoformat() + 'Z'
index_str = dt.strftime(index,'%Y-%m-%d')

day_after_index = index + datetime.timedelta(1)
day_after_index_midnight = day_after_index.replace(hour=0, minute=1)
day_after_index_formatted = day_after_index_midnight.isoformat() + 'Z'

# Init browser
init(index_str)
from common import b as b

# Setup gcal
gcal.init(index_formatted, day_after_index_formatted)
from gcal import event_list as event_list

######################
# Update old entries #
######################
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
i = 1

no_project_txt = open("no_project/{}.txt".format(index_str), "w")

for event in event_list: # Skip ith event, avoid sleep from day before
    if i == 1:
        i = i+1
        continue
    else:
        if event[0] in event_exclude:
            print("{} is an excluded event, not adding".format(event[0]))
        elif event[0] in task_project_pairs:
            print("{} not found in entry-list, adding".format(event_list))
            add_entry(name=event[0], start_time=event[1], end_time=event[2],
                        project=task_project_pairs[event[0]], planned=False)
        else:
            print("{} not found in entry-list, adding".format(event_list))
            add_entry(name=event[0], start_time=event[1], end_time=event[2],
                        project=None, planned=False)
            no_project_txt.write(str(event[0]))

b.quit()
no_project_txt.close()
