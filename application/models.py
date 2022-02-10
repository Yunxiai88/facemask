import os
import json
import pathlib

path = pathlib.Path(__file__)

def save(date, message):
    filename = os.path.join(str(path.parent.parent), "webapp/data/summary.json")

    # open summary file
    with open(filename,'r+') as file:
        data = json.load(file)
        # append or update info
        if (date in data) and data[date]:
            messages = data[date]
            if message not in messages:
                messages.append(message)
                data.update({date: messages})
        else:
            data.update({date: [message]})
    
    with open(filename, 'w') as file:
        # set file's current position at offset.
        #file.seek(0)
        json.dump(data, file, indent = 4)