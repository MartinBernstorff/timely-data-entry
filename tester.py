task_project_pairs = {
    "Wake up + shower": "Morn",
    "Meditate + breakfast": "Morn",
    "Undervisermøde": "Epi",
    "Morgen-konf.": "Psychiatry-clinic",
    "Mid-day meditation": "Rest",
    "Købe ind": "Miscel",
    "Dinner": "Food",
    "Lunch": "Food",
    "Review & plan": "Daily review"
}

event_list = [['Wake up + shower', '2018-10-03T06:00:00+02:00', '2018-10-03T06:30:00+02:00']]

for event in event_list: # Skip ith event, avoid sleep from day before
    if event[0] in task_project_pairs:
        print(task_project_pairs[event[0]])
    else:
        print("Not found")
