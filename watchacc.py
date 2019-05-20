import datetime as dt
import tkinter as tk
from tkinter import filedialog
import json

dataKeys = ["nickname", \
            "manufacturer", \
            "model_name", \
            "model_number", \
            "serial_number", \
            "data"]

def save_file(watch, filePath):
    with open(filePath, 'w') as outFile:
        json.dump(watch, outFile)

def input_yesno(prompt, default):
    yes = set(['yes', 'y'])
    no = set(['no', 'n'])
    choice = input(prompt)
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        return default

def input_int(prompt, options, cancel = False):
    numOptions = len(options)

    while True:
        print(prompt)
        i = 1
        for item in options:
            print("({}) {}".format(str(i), item))
            i += 1
        if cancel:
            print("({}) CANCEL".format(numOptions + 1))
        
        try:
            choice = int(input(""))
        except(ValueError, NameError):
            print("\nError: Invalid input\n")
            continue
        
        if cancel:
            if choice < 1 or choice > numOptions + 1:
                print("\nError: Invalid selection\n")
            elif choice == numOptions + 1:
                return None
            else:
                return choice
        else:
            if choice < 1 or choice > numOptions:
                print("\nError: Invalid selection\n")
            else:
                return choice

print("Welcome to the Watch Accuracy Tester!\n")
fileOpt = input_int("Select File Option", ["Open watch file", "Start new watch file"])

root = tk.Tk()
root.withdraw()

if fileOpt == 1:
    print("\nOpening File Dialog...")
    filePath = filedialog.askopenfilename(initialdir = "./", \
                                          title = "Open file", \
                                          filetypes = (("watch files","*.wat"),("all files","*.*")))
    try:
        watch = json.loads(open(filePath).read())
    except:
        print("\nError: File is formatted incorrectly or corrupted, and could not be read.\n")
        exit()
    
    print("Opened " + watch['nickname'] + " data file.")

elif fileOpt == 2:
    watch = {}
    print("")
    for key in dataKeys:
        watch[key] = input("{}: ".format(key))

    print("\nOpening File Dialog...")
    filePath = filedialog.asksaveasfilename(confirmoverwrite = True, \
                                            initialdir = "./", \
                                            initialfile = watch['nickname'], \
                                            title = "Save file", \
                                            defaultextension = ".wat", \
                                            filetypes = (("watch files","*.wat"),("all files","*.*")))

    save_file(watch, filePath)

while True:
    print("")
    actionOpt = input_int("Select Option", ["New measurement", \
                                            "Change watch information", \
                                            "View raw data", \
                                            "Save watch file", \
                                            "Exit"])

    if actionOpt == 1:
        print("")
        reset = input_yesno("Have you adjusted your watch time since the last measurement? (y/N)", False)

    elif actionOpt == 2:
        print("")

        currentInfo = []
        for key in dataKeys:
            currentInfo.append("{}: {}".format(key, watch[key]))

        infoOpt = input_int("Change which item?", currentInfo, cancel = True)

        if infoOpt == None:
            print("Cancelled.")
        else:
            watch[dataKeys[infoOpt]] = input("Enter new value for {}: ".format(dataKeys[infoOpt]))
    
    elif actionOpt == 3:
        print("")
        for key in dataKeys:
            print("{}: {}".format(key, watch[key]))
    
    elif actionOpt == 4:
        save_file(watch, filePath)
        print("\nSaved to {}".format(filePath))
    
    elif actionOpt == 5:
        exit()