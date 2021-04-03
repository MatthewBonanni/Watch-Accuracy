import ntplib
import datetime as dt
import time
import dateutil.parser
import tabulate
import tkinter as tk
from tkinter import filedialog
import os
import json

# Required fields in a watch file
watchKeys = ["nickname", \
             "manufacturer", \
             "model_name", \
             "model_number", \
             "serial_number", \
             "data"]

# Data items stored with each measurement
dataKeys = ["utc", \
            "measured", \
            "offset", \
            "offset_change", \
            "t_elapsed_split", \
            "t_elapsed_total", \
            "t_human", \
            "rate"]

# Data which is calculated, not directly measured
dataKeys_notMeasured = ["offset_change", \
                        "t_elapsed_split", \
                        "t_elapsed_total", \
                        "t_human", \
                        "rate"]

# Connects to the window server
def start_tk():
    while True:
        try:
            root = tk.Tk()
            root.withdraw()
            break
        except:
            input("Window server not available. Press Enter to try again...")

# Determines the directory where the script is located
def get_appDir():
    try:
        appDir = os.path.dirname(os.path.abspath(__file__))
    except:
        appDir = os.getcwd()
    
    return appDir

# Loads the application data if the corresponding file exists. Creates it if not.
def load_appData(appDir):
    try:
        appData = json.loads(open(appDir + '/appData.dat').read())
    except:
        appData = {}
        appData['prevDir'] = appDir
        appData['prevFile'] = ""

    return appData

# Writes to the given application data file and exits the script
def quit_app(appDir):
    with open(appDir + '/appData.dat', 'w') as dataFile:
        json.dump(appData, dataFile)
    exit()

# Writes the given watch data to the given file
def save_file(watch, filePath):
    appData['prevDir'], appData['prevFile'] = os.path.split(filePath)
    with open(filePath, 'w') as outFile:
        json.dump(watch, outFile)

# Constructs yes or no dialog menu
def input_yesno(prompt, default):
    yes = set(['yes', 'y'])
    no = set(['no', 'n'])
    
    if default:
        ynStr = "(Y/n)"
    else:
        ynStr = "(y/N)"

    choice = input(prompt + " {0}: ".format(ynStr))
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        return default

# Constructs numerical choice dialog menu
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
            choice = int(input("Select: "))
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

# Gets the current UTC time and computes the offset of the measured time
def measure_offset():
    input("Press Enter when the seconds hand reaches the 12 o'clock position...")

    # Get UTC time
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
            input("Failed to connect to NTP server.\nPress Enter to try again when the seconds hand reaches 12...")
    
    # Estimate the measured time by rounding to the closest minute
    nearest_min = dt.timedelta(minutes = round(realTime.second/60))
    measuredTime = realTime.replace(second = 0, microsecond = 0) + nearest_min

    # Allow the user to adjust the time in minute increments as necessary
    while True:
        timeCorrect = input_yesno("Your watch should read UTC {0}. Is this correct?".format(measuredTime), default=True)

        if not timeCorrect:
            try:
                adjust = float(input("Enter the amount (in minutes) to adjust this time: "))
                adjustTimeDelta = dt.timedelta(minutes = adjust)
                measuredTime = measuredTime + adjustTimeDelta
                continue
            except(ValueError, NameError):
                print("\nError: Invalid input\n")
        else:
            break
    
    # Write data to memory
    offset = (measuredTime - realTime).total_seconds()
    
    measurement = {}
    measurement['utc'] = [realTime.isoformat()]
    measurement['measured'] = [measuredTime.isoformat()]
    measurement['offset'] = [offset]

    print("\nMeasurement recorded. Please wait approximately 12 hours before taking another measurement.")

    return measurement

###################################################################################################

# Startup sequence
appDir = get_appDir()
appData = load_appData(appDir)

print("\
 _       __      __       __    ____            ____\n\
| |     / /___ _/ /______/ /_  / __ \___  _____/ __/\n\
| | /| / / __ `/ __/ ___/ __ \/ /_/ / _ \/ ___/ /_  \n\
| |/ |/ / /_/ / /_/ /__/ / / / ____/  __/ /  / __/  \n\
|__/|__/\__,_/\__/\___/_/ /_/_/    \___/_/  /_/     \n\
")
print("Created by Matthew R. Bonanni\n")
print("Welcome to the Watch Accuracy Tester!")

# File open/create menu
while True:
    fileOpt = input_int("Select File Option:", ["Open watch file", "Start new watch file", "Quit"])

    # Open existing watch file
    if fileOpt == 1:

        # Select file via GUI
        print("\nOpening File Dialog...")
        start_tk()
        filePath = filedialog.askopenfilename(initialdir = appData['prevDir'], \
                                              initialfile = appData['prevFile'], \
                                              title = "Open file", \
                                              filetypes = (("watch files","*.wat"),("all files","*.*")))
        
        # Open file if possible
        try:
            watch = json.loads(open(filePath).read())
            print("Opened " + watch['nickname'] + " data file.")
            break
        except:
            print("\nFile could not be read.\n")
    
    # Create new watch file
    elif fileOpt == 2:

        # Manually set all fields except data
        watch = {}
        print("")
        for key in watchKeys:
            if key != 'data':
                watch[key] = input("{0}: ".format(key))
    
        watch['data'] = ""

        # Select file via GUI
        print("\nOpening File Dialog...")
        start_tk()
        filePath = filedialog.asksaveasfilename(confirmoverwrite = True, \
                                                initialdir = appData['prevDir'], \
                                                initialfile = watch['nickname'], \
                                                title = "Save file", \
                                                defaultextension = ".wat", \
                                                filetypes = (("watch files","*.wat"),("all files","*.*")))
        
        # Save newly made file if possible
        try:
            save_file(watch, filePath)
            print("\nNew watch saved to: " + filePath)
            break
        except:
            print("\nNo file saved.\n")
    
    # Quit application
    elif fileOpt == 3:
        quit_app(appDir)

# Watch management menu
while True:
    print("")
    actionOpt = input_int("Select Option", ["New measurement", \
                                            "View past measurement data", \
                                            "Delete last measurement", \
                                            "Analyze performance", \
                                            "View/Change watch information", \
                                            "Save watch file", \
                                            "Save and exit", \
                                            "Exit without saving"])
    
    # Take new measurement
    if actionOpt == 1:

        # Ask whether to add to current series or start new series
        print("")
        if watch['data'] != "":
            newSeries = input_yesno("Have you adjusted your watch time since the last measurement?", False)
        else:
            newSeries = True
        
        # Take measurement
        dataPt = measure_offset()

        # Create new series
        if newSeries:

            # Create first series or append new series
            if watch['data'] == "":
                watch['data'] = [dataPt]
            else:
                watch['data'].append(dataPt)

            # Initialize multi-measurement computable values
            watch['data'][-1]['offset_change'] = [0]
            watch['data'][-1]['t_elapsed_split'] = [0]
            watch['data'][-1]['t_elapsed_total'] = [0]
            watch['data'][-1]['t_human'] = [str(dt.timedelta(seconds = 0))]
            watch['data'][-1]['rate'] = [None]
        
        # Add measurement to current series
        else:

            # Compute multi-measurement values
            dataPt_calc = {}

            dataPt_calc['offset_change'] = dataPt['offset'][0] - watch['data'][-1]['offset'][-1]

            first_datetime = dateutil.parser.parse(watch['data'][-1]['utc'][0])
            prev_datetime = dateutil.parser.parse(watch['data'][-1]['utc'][-1])
            new_datetime = dateutil.parser.parse(dataPt['utc'][0])

            dataPt_calc['t_elapsed_split'] = (new_datetime - prev_datetime).total_seconds()
            dataPt_calc['t_elapsed_total'] = (new_datetime - first_datetime).total_seconds()
            dataPt_calc['t_human'] = str(new_datetime - first_datetime)
            
            dataPt_calc['rate'] = dataPt_calc['offset_change'] / (dataPt_calc['t_elapsed_split'] / 86400)

            # Append measurement to last series
            for key in watch['data'][-1]:
                if key not in dataKeys_notMeasured:
                    watch['data'][-1][key].append(dataPt[key][0])
                else:
                    watch['data'][-1][key].append(dataPt_calc[key])
    
    # View past measurement data
    elif actionOpt == 2:
        if watch['data'] == "":
            print("\nNo data saved.")
            continue
        else:
            for series in watch['data']:
                seriesTable = [dataKeys]
                for i in range(len(series['measured'])):
                    row = []
                    for key in dataKeys:
                        row.append(series[key][i])
                    seriesTable.append(row)
                
                print("")
                print(tabulate.tabulate(seriesTable, headers = 'firstrow', tablefmt = 'simple'))
    
    # Delete the last measurement
    elif actionOpt == 3:
        if watch['data'] == "":
            print("\nNo data exists to delete.")
            continue
        
        confirmDeleteOpt = input_yesno("\nAre you sure you want to delete the last data point?", False)
        if confirmDeleteOpt:
            if len(watch['data']) == 1 and len(watch['data'][0]['measured']) == 1:
                watch['data'] = ""
            elif len(watch['data'][-1]['measured']) == 1:
                del watch['data'][-1]
            else:
                for key in watch['data'][-1]:
                    del watch['data'][-1][key][-1]
        else:
            print("Delete operation cancelled.")
            continue
    
    # Analyze the watch performance based on data in memory
    elif actionOpt == 4:

        # Verify at least 1 series
        if watch['data'] == "":
            print("\nA minimum of 1 series with 2 data points is required for analysis.")
            continue
        
        # Verify at least 2 data points
        seriesWith2 = 0
        for series in watch['data']:
            if len(series['rate']) >= 2:
                seriesWith2 += 1
        
        if seriesWith2 == 0:
            print("\nA minimum of 1 series with 2 data points is required for analysis.")
            continue
        
        # Compute total elapsed time across all series
        totalTime = 0
        elapsedTimeWarning = 0

        for series in watch['data']:
            if len(series['rate']) >= 2:
                if (series['t_elapsed_total'][-1] / 3600) < 12:
                    elapsedTimeWarning = 1
                totalTime += series['t_elapsed_total'][-1]
        
        # Compute weighted average of offset rate
        # Each measurement is weighted by its split duration
        meanRate = 0

        for series in watch['data']:
            numPts = len(series['rate'])
            if numPts >= 2:
                for i in range(1,numPts):
                    weight = series['t_elapsed_split'][i] / totalTime
                    meanRate += series['rate'][i] * weight

        if elapsedTimeWarning:
            print("\nWarning: For accurate performance analysis, series data should span at least 12 hours.")
        
        print("\nTime-weighted mean deviation rate is {0} seconds per day.".format(meanRate))
    
    # View or edit the watch metadata
    elif actionOpt == 5:
        print("")

        # Print current metadata
        currentInfo = []
        for key in watchKeys:
            if key != 'data':
                currentInfo.append("{0}: {1}".format(key, watch[key]))
        
        # Edit data menu
        infoOpt = input_int("Change which item?", currentInfo, cancel = True)

        if infoOpt == None:
            print("Cancelled.")
            continue
        else:
            watch[watchKeys[infoOpt-1]] = input("Enter new value for {0}: ".format(watchKeys[infoOpt-1]))
    
    # Save without quitting
    elif actionOpt == 6:
        save_file(watch, filePath)
        print("\nSaved to {0}".format(filePath))
    
    # Save and quit
    elif actionOpt == 7:
        save_file(watch, filePath)
        print("\nSaved to {0}".format(filePath))
        quit_app(appDir)
    
    # Quit without saving
    elif actionOpt == 8:
        confirmExitOpt = input_yesno("\nAre you sure you want to exit without saving?", False)
        if confirmExitOpt:
            quit_app(appDir)
        else:
            continue