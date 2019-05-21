import ntplib
import datetime as dt
import time
import tabulate
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
    
    if default:
        ynStr = "(Y/n)"
    else:
        ynStr = "(y/N)"

    choice = input(prompt + " {0}\n".format(ynStr))
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
            print("({0!s}) {1}".format(str(i), item))
            i += 1
        if cancel:
            print("({0}) CANCEL".format(numOptions + 1))
        
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

def measure_offset():
    input("Press Enter when the seconds hand reaches the 12 o'clock position...")
    while True:
        try:
            ntp = ntplib.NTPClient()
            ntpserver = "europe.pool.ntp.org"
            t0 = time.perf_counter()
            rawTime = dt.datetime.utcfromtimestamp(ntp.request(ntpserver).tx_time)
            pingTime = time.perf_counter() - t0
            pingDifference = dt.timedelta(seconds = (pingTime / 2))
            realTime = rawTime + pingDifference
            print("Official UTC time per {0}: {1}".format(ntpserver, realTime))
            break
        except:
            input("Failed to connect to NTP server. Press Enter to try again.")
          
    nearest_min = dt.timedelta(minutes = round(realTime.second/60))
    measuredTime = realTime.replace(second = 0, microsecond = 0) + nearest_min
    timeCorrect = input_yesno("Your watch should read {0}. Is this correct?".format(measuredTime), True)
    
    measurement = {}
    measurement['utc'] = [realTime.isoformat()]
    measurement['measured'] = [measuredTime.isoformat()]

    return measurement

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
        if key != 'data':
            watch[key] = input("{0}: ".format(key))
    
    watch['data'] = ""

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
                                            "View/Change watch information", \
                                            "View past measurement data", \
                                            "Save watch file", \
                                            "Save and exit", \
                                            "Exit without saving"])

    if actionOpt == 1:
        print("")
        if fileOpt == 1 and watch['data'] != "":
            newSeries = input_yesno("Have you adjusted your watch time since the last measurement?", False)
        else:
            newSeries = True
        
        dataPt = measure_offset()

        if newSeries:
            if watch['data'] == "":
                watch['data'] = [dataPt]
            else:
                watch['data'].append(dataPt)
        else:
            watch['data'][-1]['utc'].append(dataPt['utc'][0])
            watch['data'][-1]['measured'].append(dataPt['measured'][0])

    elif actionOpt == 2:
        print("")

        currentInfo = []
        for key in dataKeys:
            if key != 'data':
                currentInfo.append("{0}: {1}".format(key, watch[key]))

        infoOpt = input_int("Change which item?", currentInfo, cancel = True)

        if infoOpt == None:
            print("Cancelled.")
        else:
            watch[dataKeys[infoOpt]] = input("Enter new value for {0}: ".format(dataKeys[infoOpt]))
    
    elif actionOpt == 3:
        for dataSeries in watch['data']:
            print("")
            print(tabulate.tabulate(dataSeries, headers = 'keys', tablefmt = 'simple'))
    
    elif actionOpt == 4:
        save_file(watch, filePath)
        print("\nSaved to {0}".format(filePath))
    
    elif actionOpt == 5:
        save_file(watch, filePath)
        print("\nSaved to {0}".format(filePath))
        exit()
    
    elif actionOpt == 6:
        confirmExitOpt = input_yesno("\nAre you sure you want to exit without saving?", False)
        if confirmExitOpt:
            exit()