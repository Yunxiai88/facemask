import os
import csv
import json
import pathlib

path = pathlib.Path(__file__)

def getFiles() :
    file_path = "./application/static/processed"

    file_list = []

    if not os.path.exists(file_path):
        print("folder for this user not exists")
    else:
        count = 0
        for file in os.listdir(file_path):
            # fetch max two images
            if count >= 2:
                break
            
            file_list.append(file)
            count += 1
    return file_list

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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