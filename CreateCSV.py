import re
import csv
import os, shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

# This script takes in the raw whatsapp text files in the raw_text_files directory,
# and transforms it into a pandas-friendly CSV, which it deposits in csv_output.

# ASSUMPTION: This is the first script run, and this script is always run before Analyse.py
# Clears all relevant directories to remove traces of any previous times the program has been run
def clear():

    folders = ['images', 'csv_output/tables/individual_common_words', 'csv_output/tables/individual_per_message']
    for folder in folders:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

def startsWithDate(s):
    # Note - only works in dd/mm/yy and 12-hour time format
    pattern = '^([1]?\d)(\/)([1-3]?\d)(\/)(\d\d), ([0-1]?\d):(\d\d) (AM|PM) -'
    result = re.match(pattern, s)
    if result:
        return True
    return False

# Invariant: Author should be the first thing in given line
def startsWithAuthor(s):
    patterns = [
        '([\w]+):',  # First Name
        '([\w]+[\s]+[\w]+):',  # First Name + Last Name
        '([\w]+[\s]+[\w]+[\s]+[\w]+):',  # First Name + Middle Name + Last Name
        '([+]\d{2} \d{5} \d{5}):',  # Mobile Number (India)
        '([+]\d{2} \d{3} \d{3} \d{4}):',  # Mobile Number (US)
        '([+]\d{2} \d{4} \d{7}):'  # Mobile Number (Europe)
    ]
    pattern = '^' + '|'.join(patterns)
    result = re.match(pattern, s)
    if result:
        return True
    return False


# example line = 18/06/17, 22:47 - Loki: Why do you have 2 numbers, Banner?
# separates and returns the date, time author and message of the line
def getDataPoint(line):
    splitLine = line.split(' - ')
    dateTime = splitLine[0]
    date, time = dateTime.split(', ')
    message = ' '.join(splitLine[1:])

    if startsWithAuthor(message):
        splitMessage = message.split(':')
        author = splitMessage[0]
        message = ' '.join(splitMessage[1:])
    else:
        author = None
    return date, time, author, message

def createCSV():
    root = tk.Tk()
    root.withdraw()
    readFile = filedialog.askopenfilename()
    # readFile = Path("raw_text_files/grounders.txt")
    csvOut = Path("csv_output/dataframe.csv")

    with open(csvOut, mode='w', encoding="utf8", newline='') as out, open(readFile, encoding="utf8") as raw:
        out = csv.writer(out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        out.writerow(['Date', 'Time', 'Author', 'Message'])  # write csv column names

        raw.readline()  # skip first line of raw text - contains useless info about encryption

        # store a line to ensure loop invariant - always has line info stored
        firstLine = raw.readline().strip()
        date, time, author, message = getDataPoint(firstLine)

        for line in raw:
            line = line.strip() # Destroys leading/trailing whitespaces
            message = message.strip()
            if startsWithDate(line):  # new message - not multi-line
                out.writerow([date, time, author, message])
                date, time, author, message = getDataPoint(line)
            else:
                message = message + line

def main():
    clear()
    createCSV()


if __name__ == "__main__":
    main()
