# Other imports
import time
import datetime
from datetime import datetime as dt

# Get task_dicts
from task_dicts import task_project_pairs, event_exclude, task_tags

# Import helper functions
from common import *
import gcal

#Generate tomorrow-string
index = dt.today() + datetime.timedelta(1) #<--- Beware the time-delta!
index_midnight = index.replace(hour=0, minute=1)
index_formatted = index_midnight.isoformat() + 'Z'
index_str = dt.strftime(index,'%Y-%m-%d')

day_after_index = index + datetime.timedelta(1)
day_after_index_midnight = day_after_index.replace(hour=0, minute=1)
day_after_index_formatted = day_after_index_midnight.isoformat() + 'Z'

######################
# Let's start entry! #
######################
# Init browser
init(index_str)
from common import b

# Setup gcal
gcal.init(index_formatted, day_after_index_formatted)
from gcal import event_list

###############
# Add entries #
###############

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
            if event[0] in task_tags:
                add_entry(name=event[0], start_time=event[1], end_time=event[2],
                            project=task_project_pairs[event[0]],
                            tags=task_tags[event[0]])
            else:
                add_entry(name=event[0], start_time=event[1], end_time=event[2],
                            project=task_project_pairs[event[0]])
        else:
            if event[0] in task_tags:
                add_entry(name=event[0], start_time=event[1], end_time=event[2],
                            tags=task_tags[event[0]])
                no_project_txt.write(str(event[0]) + "\n")
            else:
                add_entry(name=event[0], start_time=event[1], end_time=event[2])
                no_project_txt.write(str(event[0]) + "\n")

b.quit()
no_project_txt.close()
