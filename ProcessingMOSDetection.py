import csv
import datetime as dt
import getpass
import math
import os

import matplotlib.dates
import numpy as np
import scipy.signal
from scipy import signal
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta

from os import listdir
from os.path import isfile, join

import pandas as pd
import scipy.stats as sp

########################################################################################################################
########################################################################################################################
# Define functions and mehods:

# This function reads from csv file and returns the list of values
def readEDADataFromCSV(filepath):
    edaData = []
    with open(filepath, encoding="utf8") as f:
        csv_reader = csv.reader(f)
        for line_no, line in enumerate(csv_reader, 1):
            if line_no == 1:  # get time from headers of csv file
                csvTime = getTimeFromCSVFile(str(line[0]))
            if line_no > 3: # skip headers of csv file
                edaData.append(float(line[0]))
    return edaData, csvTime

# This function converts the time given in the csv format to time: https://stackoverflow.com/questions/3682748/converting-unix-timestamp-string-to-readable-date
def getTimeFromCSVFile(s):
    s1, s2 = s.split('.')
    ts = int(s1)
    # print(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
    csvTime = datetime.utcfromtimestamp(ts)
    csvTime = csvTime - timedelta(hours=7) # change it to time in California
    return csvTime

# This function applies the filtering to the given EDA raw signal according to the paper
def butterWorthFiltering(edaSignal):
    fc1 = 5 # cutoff frequency for low pass filter
    fs = 12 # sampling frequency
    b1, a1 = signal.butter(1, fc1/(fs/2), 'low') # create first order Butterworth filter at low freq
    fc2 = 0.05 # cutoff frequency for high pass filter
    b2, a2 = signal.butter(1, fc2 / (fs / 2), 'high')  # create first order Butterworth filter at high freq
    edaFilteredLow = signal.lfilter(b1, a1, edaSignal) # apply low pass filter
    edaFilteredHigh = signal.lfilter(b2, a2, edaFilteredLow)  # apply high pass filter
    return edaFilteredHigh
# This function gets the peaks from a given signal
def getLocalMinimaLocalMaxima(edaFiltered):
    locs, _ = scipy.signal.find_peaks(edaFiltered)
    pks = edaFiltered[locs]
    return locs, pks
# This function removes the local minima from the peaks detected
def removeLocalMinima(locs, pks, edaFiltered):
    pks2 = []
    locs2 = []
    gradEda = np.gradient(edaFiltered)
    for i in range(0, len(locs)):
        if locs[i] >= 1 and locs[i] < len(gradEda) - 1:
            if gradEda[locs[i] - 1] and gradEda[locs[i] + 1] < 0:
                pks2.append(pks[i])
                locs2.append(locs[i])
    return locs2, pks2
# This function gets the on sets given the peaks locations
def getOnSets(locs, edaFiltered):
    onSets = []
    onSetsLocs = []
    for i in range(0, len(locs)):
        pkLoc = locs[i]
        onSetLoc = pkLoc
        while onSetLoc >= 1 and edaFiltered[onSetLoc - 1] < edaFiltered[onSetLoc]:
            onSetLoc = onSetLoc - 1
        onSetsLocs.append(onSetLoc)
        onSets.append(edaFiltered[onSetLoc])
    return onSetsLocs, onSets
# This function applies the rules from the Paper
def getTotalScoreFromRules(locs, pks, onSetsLocs, onSets):
    sampleRate = 4  # sampling rate of Empatica Watch 4Hz
    R1 = []  # Rule 1
    R3 = []  # Rule 3
    R4 = []  # Rule 4
    TS = []  # Total Score
    w = 100 / 3  # Weight applied to each rule
    for i in range(0, len(locs)):
        n = locs[i] - onSetsLocs[i]
        # Rule 1
        if 2 * sampleRate <= n and n <= 5 * sampleRate:
            R1.append(1)
        elif 5 * sampleRate < n and n <= 8 * sampleRate:
            R1.append(0.5)
        else:
            R1.append(0)
        # Rule 3
        if 1 * sampleRate <= n and n <= 2 * sampleRate:
            R3.append(1)
        elif 5 * sampleRate < n and n <= 15 * sampleRate:
            R3.append(0.5)
        else:
            R3.append(0)
        # Rule 4
        if n != 0:
            dg = pks[i] - onSets[i]
            RS = math.atan(dg / n) * 180 / math.pi
            if RS >= 10:
                R4.append(1)
            elif 8 <= RS and RS < 10:
                R4.append(0.5)
            else:
                R4.append(0)
        TS.append(R1[i] * w + R3[i] * w + R4[i] * w)
    # Get critical scores after applying rules
    totalScore = np.asarray(TS)
    indexCS = np.where(totalScore >= 2 * w)[0]
    pksCS = np.asarray(pks)
    pksCS = list(pksCS[indexCS])
    locsCS = np.asarray(locs)
    locsCS = list(locsCS[indexCS])
    countMOSDetected = len(locsCS)
    return countMOSDetected, locsCS, pksCS

# This function maps a given index to datetime by knowing that sampling frequency is 4Hz
def mapIndexToTime(csvTime, index):
    index = index + 1
    ts = int(round(index/4))
    indexTime = csvTime + timedelta(seconds=ts)
    return indexTime

# This function creates a list with all the timestamps of a given edaSignal
def createTimeStamps(edaSignal, csvTime):
    timeStamps = []
    for i in range(0, len(edaSignal)):
        timeStamps.append(mapIndexToTime(csvTime, i))
    return timeStamps

# This function returns an array of signals that correspond to the workday only (between 8am-7pm)
def getSignalDuringWorkingTimeOnly(edaSignal, csvTime):
    startWorkingTime = dt.time(8, 0, 0, 0) # hardcoded
    endWorkingTime = dt.time(19, 0, 0, 0)  # hardcoded
    timeStamps = createTimeStamps(edaSignal, csvTime)
    days = getDaysFromTimeStamps(timeStamps)
    workingTimeTSDays = []
    for i in range(0, len(days)):
        flagStart = True
        startTime = None
        endTime = None
        for j in range(0, len(timeStamps)):
            if timeStamps[j].date() == days[i]:
                if timeStamps[j].time() >= startWorkingTime and timeStamps[j].time() <= endWorkingTime:
                    if flagStart:
                        flagStart = False
                        startTime = timeStamps[j].time()
                    endTime = timeStamps[j].time()
        if startTime is not None:
            workingTimeTSDays.append([days[i], startTime, endTime])
    edaSignalsList = []
    csvTimeList = []
    for i in range(0, len(workingTimeTSDays)):
        startTime = dt.datetime.combine(workingTimeTSDays[i][0], workingTimeTSDays[i][1])
        endTime = dt.datetime.combine(workingTimeTSDays[i][0], workingTimeTSDays[i][2])
        idxStart = timeStamps.index(startTime)
        idxEnd = timeStamps.index(endTime)
        edaSignalsList.append(edaSignal[idxStart:idxEnd+1])
        csvTimeList.append(startTime)
        # progress until here -----------------------------------------------------------
    return edaSignalsList, csvTimeList

def getDaysFromTimeStamps(timeStamps):
    days = []
    for i in range(0, len(timeStamps)):
        day = timeStamps[i].date()
        if day in days:
            continue
        else:
            days.append(day)
    return days


# This function detects the MoS of a given EDA csv file and computes the accumulated MoS
def getAccumulatedMoS(edaSignal, csvTime):
    # STEP 1: Read csv file and create a list of EDA values, then plot it
    #filename = r'D:\Files\Downloads\MoSDetection\EDAValues\EDA9.csv'
    #edaSignal, csvTime = readEDADataFromCSV(filename)  # read the signal from csv file
    x = range(0, len(edaSignal))  # create the x axis of the signal
    # STEP 2: Filter the data using Butterworth filter and plot the filtered signal
    edaFiltered = butterWorthFiltering(edaSignal)
    # STEP 3: Find local minima and local maxima and plot them
    locs, pks = getLocalMinimaLocalMaxima(edaFiltered)
    # STEP 4: Remove local minima from the data
    locs, pks = removeLocalMinima(locs, pks, edaFiltered)
    # STEP 5: Get on set for every peak and its location
    onSetsLocs, onSets = getOnSets(locs, edaFiltered)
    # STEP 6: Apply rules according to Paper
    countMOSDetected, locsCS, pksCS = getTotalScoreFromRules(locs, pks, onSetsLocs, onSets)
    # STEP 7: Map index to time and compute the accumulated MOS
    timeAccumulatedMoS = []
    for i in range(0, len(locsCS)):
        indexTime = mapIndexToTime(csvTime, locsCS[i])
        timeAccumulatedMoS.append(indexTime)
    # Get accumulated data
    accumulatedMOS = []
    for i in range(0, len(locsCS)):
        accumulatedMOS.append(i + 1)
    return timeAccumulatedMoS, accumulatedMOS

# This function detects the MoS of a given EDA csv file and computes the accumulated MoS
def getAccumulatedMoSHourly(edaSignal, csvTime):
    # STEP 1: Read csv file and create a list of EDA values, then plot it
    #filename = r'D:\Files\Downloads\MoSDetection\EDAValues\EDA9.csv'
    #edaSignal, csvTime = readEDADataFromCSV(filename)  # read the signal from csv file
    x = range(0, len(edaSignal))  # create the x axis of the signal
    # STEP 2: Filter the data using Butterworth filter and plot the filtered signal
    edaFiltered = butterWorthFiltering(edaSignal)
    # STEP 3: Find local minima and local maxima and plot them
    locs, pks = getLocalMinimaLocalMaxima(edaFiltered)
    # STEP 4: Remove local minima from the data
    locs, pks = removeLocalMinima(locs, pks, edaFiltered)
    # STEP 5: Get on set for every peak and its location
    onSetsLocs, onSets = getOnSets(locs, edaFiltered)
    # STEP 6: Apply rules according to Paper
    countMOSDetected, locsCS, pksCS = getTotalScoreFromRules(locs, pks, onSetsLocs, onSets)
    # STEP 7: Map index to time and compute the accumulated MOS
    timeAccumulatedMoSHourly = []
    for i in range(0, 11): # hardcoded
        timeAccumulatedMoSHourly.append(8 + i)
    # for i in range(0, len(locsCS)):
    #     indexTime = mapIndexToTime(csvTime, locsCS[i])
    #     timeAccumulatedMoS.append(indexTime)
    # Get accumulated data
    # accumulatedMOSHourly = []
    # startTime = mapIndexToTime(csvTime, locsCS[0]) # hardcoded
    # accum = 0
    # for i in range(0, len(locsCS)):
    #     indexTime = mapIndexToTime(csvTime, locsCS[i])
    #     endTime = startTime + timedelta(hours=1)
    #     if startTime.time() <= indexTime.time() and indexTime.time() <= endTime.time():
    #         accum = accum + 1
    #     else:
    #         timeAccumulatedMoSHourly.append(indexTime.time())
    #         accumulatedMOSHourly.append(accum + 1)
    #         accum = 0
    #         startTime = startTime + timedelta(hours=1)
    #
    # indexTime = mapIndexToTime(csvTime, locsCS[len(locsCS) - 1])
    # timeAccumulatedMoSHourly.append(indexTime.time())
    # accumulatedMOSHourly.append(accum + 1)
    accumulatedMOSHourly = []
    for i in range(0, 11): # hardcoded
        accumulatedMOSHourly.append(0)
    for i in range(0, len(locsCS)): # hardcoded
        indexTime = mapIndexToTime(csvTime, locsCS[i])
        if dt.time(8, 0, 0, 0) <= indexTime.time() and indexTime.time() <= dt.time(9, 0, 0, 0):
            accumulatedMOSHourly[0] = accumulatedMOSHourly[0] + 1
        elif dt.time(9, 0, 0, 0) <= indexTime.time() and indexTime.time() <= dt.time(10, 0, 0, 0):
            accumulatedMOSHourly[1] = accumulatedMOSHourly[1] + 1
        elif dt.time(10, 0, 0, 0) <= indexTime.time() and indexTime.time() <= dt.time(11, 0, 0, 0):
            accumulatedMOSHourly[2] = accumulatedMOSHourly[2] + 1
        elif dt.time(11, 0, 0, 0) <= indexTime.time() and indexTime.time() <= dt.time(12, 0, 0, 0):
            accumulatedMOSHourly[3] = accumulatedMOSHourly[3] + 1
        elif dt.time(12, 0, 0, 0) <= indexTime.time() and indexTime.time() <= dt.time(13, 0, 0, 0):
            accumulatedMOSHourly[4] = accumulatedMOSHourly[4] + 1
        elif dt.time(13, 0, 0, 0) <= indexTime.time() and indexTime.time() <= dt.time(14, 0, 0, 0):
            accumulatedMOSHourly[5] = accumulatedMOSHourly[5] + 1
        elif dt.time(14, 0, 0, 0) <= indexTime.time() and indexTime.time() <= dt.time(15, 0, 0, 0):
            accumulatedMOSHourly[6] = accumulatedMOSHourly[6] + 1
        elif dt.time(15, 0, 0, 0) <= indexTime.time() and indexTime.time() <= dt.time(16, 0, 0, 0):
            accumulatedMOSHourly[7] = accumulatedMOSHourly[7] + 1
        elif dt.time(16, 0, 0, 0) <= indexTime.time() and indexTime.time() <= dt.time(17, 0, 0, 0):
            accumulatedMOSHourly[8] = accumulatedMOSHourly[8] + 1
        elif dt.time(17, 0, 0, 0) <= indexTime.time() and indexTime.time() <= dt.time(18, 0, 0, 0):
            accumulatedMOSHourly[9] = accumulatedMOSHourly[9] + 1
        elif dt.time(18, 0, 0, 0) <= indexTime.time() and indexTime.time() <= dt.time(19, 0, 0, 0):
            accumulatedMOSHourly[10] = accumulatedMOSHourly[10] + 1


    return timeAccumulatedMoSHourly, accumulatedMOSHourly

def getTimeOnlyWithMainDate(mainDate, timeAccumulatedMoS):
    timeOnly = []
    for i in range(0, len(timeAccumulatedMoS)):
        timeOnly.append(dt.datetime.combine(mainDate, timeAccumulatedMoS[i].time()))
    return  timeOnly

def getNPArrayTimeOnly(arrayTimeOnly):
    aux = []
    for i in range(0, len(arrayTimeOnly)):
        aux.append(int(arrayTimeOnly[i].hour)*60 + int(arrayTimeOnly[i].minute))
    return np.array(aux)

def writeMoSToCSVFile(pathWorkingDir, arraccumulatedMOSHourly, csvTime, personalizedThreshold):
    fileName = 'HourlyMoS.csv'
    startingTime = int(csvTime.hour)
    f = open(join(pathWorkingDir, fileName), 'w')
    writer = csv.writer(f)
    writer.writerow(csvTime.strftime('%m/%d/%Y'))
    for i in range(0, len(arraccumulatedMOSHourly)):
        writer.writerow([str(startingTime) + ' - ' + str(startingTime + 1), arraccumulatedMOSHourly[i] - personalizedThreshold])
        startingTime = startingTime + 1;
    f.close()



########################################################################################################################
########################################################################################################################

# Compute the accumulated MOS for a bunch of files
# Luis
# pathWorkingDir = r'D:\Files\Downloads\MoSDetection\EDAValues'
# Saketh
# pathWorkingDir = r'D:\Files\SakethsData\MoSDetection\EDAValues'
# Neemish
# pathWorkingDir = r'D:\Files\NeemishsData\GSR'
# Saketh
#pathWorkingDir = r'D:\Files\SakethsData2\GSR'

# Mishel
pathWorkingDir = r'D:\Files\MishelsData\GSR'

filesList = [f for f in listdir(pathWorkingDir) if isfile(join(pathWorkingDir, f))]

plt.figure(0)

mainDate = None
arrayAccumulatedMOS = []
arrayTimeAccumulatedMoS = []
arrayTimeOnly = []
for i in range(0, len(filesList)):
    edaSignal, csvTime = readEDADataFromCSV(join(pathWorkingDir, filesList[i]))  # read the signal from csv file

    cumulativeScore = 0
    edaSignalsList, csvTimeList = getSignalDuringWorkingTimeOnly(edaSignal, csvTime)
    for j in range(0, len(edaSignalsList)):
        timeAccumulatedMoS, accumulatedMOS = getAccumulatedMoS(edaSignalsList[j], csvTimeList[j])

        if mainDate is None and len(timeAccumulatedMoS) > 0:
            mainDate = timeAccumulatedMoS[0].date()

        if mainDate is not None:
            timeOnly = getTimeOnlyWithMainDate(mainDate, timeAccumulatedMoS)
            arrayAccumulatedMOS.extend(accumulatedMOS)
            arrayTimeAccumulatedMoS.extend(timeAccumulatedMoS)
            arrayTimeOnly.extend(timeOnly)

        accumulatedMOS = [x + cumulativeScore for x in accumulatedMOS]
        if len(accumulatedMOS) > 0:
            cumulativeScore = accumulatedMOS[len(accumulatedMOS) - 1]

        # plt.plot(timeAccumulatedMoS, accumulatedMOS, '*')
        #plt.plot(timeOnly, accumulatedMOS, '*')
        #plt.gcf().autofmt_xdate()



npArrayAccumulatedMOS = np.array(arrayAccumulatedMOS)
npArrayTimeAccumulatedMoS = np.array(arrayTimeAccumulatedMoS)
npArrayTimeOnly = getNPArrayTimeOnly(arrayTimeOnly)

slope, intercept, r_value, p_value, std_err =sp.linregress(npArrayTimeOnly,npArrayAccumulatedMOS)



def myfunc(x):
  return slope * x + intercept

mymodel = list(map(myfunc, npArrayTimeOnly))

plt.scatter(npArrayTimeOnly/60, npArrayAccumulatedMOS)
plt.plot(npArrayTimeOnly/60, mymodel, color="green" )
plt.show()

print('Slope')
print(slope*60)

# plt.plot(npArrayTimeOnly, npArrayAccumulatedMOS, '*')
# plt.gcf().autofmt_xdate()
# plt.show()


# Test a given day
# Luis
# fileName = 'EDA9.csv'
#fileName = 'EDA3.csv'
# fileName = 'EDA5.csv'
# Saketh
# fileName = 'EDA14.csv'
# fileName = 'EDA4.csv'
# fileName = 'EDA6.csv'
# fileName = 'EDA10.csv'
# Neemish
# fileName = 'EDA8.csv'

# Mishel
fileName = 'EDA6.csv'
edaSignal, csvTime = readEDADataFromCSV(join(pathWorkingDir, fileName))  # read the signal from csv file
print('Day Analyzed')
print(csvTime)
edaSignalsList, csvTimeList = getSignalDuringWorkingTimeOnly(edaSignal, csvTime)
arrtimeAccumulatedMoSHourly = []
arraccumulatedMOSHourly = []
for i in range(0, len(edaSignalsList)):
    timeAccumulatedMoSHourly, accumulatedMOSHourly = getAccumulatedMoSHourly(edaSignalsList[i], csvTimeList[i])
    arrtimeAccumulatedMoSHourly.extend(timeAccumulatedMoSHourly)
    arraccumulatedMOSHourly.extend(accumulatedMOSHourly)
accum = 0

colors = []
personalizedThreshold = math.ceil(slope*60)
comparativeValues = []
timeLine = []
startingTime = int(csvTime.hour)
# startingTime = 8

# Set colors to bar plot
for i in range(0, len(arraccumulatedMOSHourly)):
    #print(str(arrtimeAccumulatedMoSHourly[i]) + ': ')
    #print(arraccumulatedMOSHourly[i])
    #accum = accum + arraccumulatedMOSHourly[i]
    timeLine.append(str(startingTime) + ' - ' + str(startingTime + 1))
    startingTime = startingTime + 1;
    comparativeValues.append(arraccumulatedMOSHourly[i] - personalizedThreshold)
    if arraccumulatedMOSHourly[i] <= personalizedThreshold:
        #print('Pass')
        colors.append('green')
    else:
        #print('Fail')
        colors.append('red')

x_pos = np.arange(len(timeLine))
# Create bars with different colors
plt.axhline(y=0.0, color='k', linestyle='-')
plt.bar(x_pos, comparativeValues, color=colors)

plt.title('Day ' + str(csvTime.date()))

# Create names on the x-axis
plt.xticks(x_pos, timeLine)

# Show graph
plt.show()


writeMoSToCSVFile(r'D:\Files\MishelsData\Results', arraccumulatedMOSHourly, csvTime, personalizedThreshold)