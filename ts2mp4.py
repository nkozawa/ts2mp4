# ts2mp4 - Convert HDZERO Goggle DVR files in TS format to MP4 files
# Author: KozakFPV  
# Copyright (C) 2024 by Nobumichi Kozawa

version = "1.0"

from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import os
import xml.etree.ElementTree as ET
import glob
import subprocess
import threading
import atexit

root = Tk()

inputPath = StringVar()
outputPath = StringVar()
timestampOpt = BooleanVar()

def main():
    global txtMsg, btnS, btnM, btn1, btn2, cTimeOpt

    frame = ttk.Frame(root, padding=10)
    fMsg = ttk.Frame(frame, padding=10)
    txtMsg = Text(fMsg, height=15, width=80)

    loadIni()

    inputPath.set(tsPath)
    outputPath.set(mpPath)
    timestampOpt.set(tsOpt)

    style = ttk.Style()
# comment out following line because 'alt' does not work with MacOS Venture and works with default theme well
    style.theme_use('alt')  # to avoid MacOS Dark mode issue with default ttk thema 'aqua'
    root.title('ts2mp4')
    frame.pack()

    fTS = ttk.Frame(frame)
    fTS.pack(anchor=W)
    btnS = ttk.Button(
        fTS, text='HDZERO MicroSD Path(TS files)', width=30,
        command=bTSGetPath)
    btnS.pack(side=LEFT)
    eIN = ttk.Entry(fTS, textvariable=inputPath, state='readonly', width=30)
    eIN.pack(side=LEFT)
    
    fMP = ttk.Frame(frame)
    fMP.pack(anchor=W)
    btnM = ttk.Button(
        fMP, text='Output path(MP4 files)', width=30,
        command=bMPGetPath)
    btnM.pack(side=LEFT)
    eOUT = ttk.Entry(fMP, textvariable=outputPath, state='readonly', width=30)
    eOUT.pack(side=LEFT)

    fTimeOpt = ttk.Frame(frame, padding=8, relief=GROOVE)
    fTimeOpt.pack(anchor=W)
    cTimeOpt = ttk.Checkbutton(fTimeOpt, text = "Use Original File Timestamps", variable = timestampOpt)
    cTimeOpt.pack(side=LEFT)

    fDO = ttk.Frame(frame)
    fDO.pack(anchor=W)
    btn1 = ttk.Button(
        fDO, text='Start, no overwrite', width=25,
        command=bStart)
    btn1.pack(side=LEFT)
    btn2 = ttk.Button(
        fDO, text='Start, overwrite all', width=25,
        command=bStartOverwrite)
    btn2.pack(side=LEFT)

    lMsg = ttk.Label(frame,text="Messages:")
    lMsg.pack(anchor=W)
    fMsg.pack(anchor=W)
    txtMsg.grid(row=0,column=0,sticky=(N, W, S, E))
    scrollbar = ttk.Scrollbar(
    fMsg,
    orient=VERTICAL,
    command=txtMsg.yview)
    scrollbar.grid(row=0,column=1,sticky=(N, S))
    txtMsg['yscrollcommand'] = scrollbar.set

    lAuthor = ttk.Label(frame, text="V"+str(version)+" by KozakFPV")
    lAuthor.pack(anchor=E)

    logMsg("==========================================")
    logMsg("= HDZero 90FPS DVR file is not supported =")
    logMsg("==========================================")
    root.mainloop()

def bTSGetPath():
    global tsPath
    tsPath = ""
    tsPath = filedialog.askdirectory(initialdir = tsPath,title="Select OpenTX Log")
    if (tsPath != ""):
        logMsg("HDZERO TS files location: "+tsPath)
        inputPath.set(tsPath)

def bMPGetPath():
    global mpPath
    mpPath = ""
    mpPath = filedialog.askdirectory(initialdir = mpPath,title="Select OpenTX Log")
    if (mpPath != ""):
        logMsg("MP4 files output location: "+mpPath)
        outputPath.set(mpPath)

def bStart():
    disableAll()
    thread = threading.Thread(target=convertTS2MP4, args=(False,))
    thread.start()

def bStartOverwrite():
    disableAll()
    thread = threading.Thread(target=convertTS2MP4, args=(True,))
    thread.start()

def logMsg(msg):
    global txtMsg
    txtMsg.insert(END, msg+"\n")
    txtMsg.see(END)

def disableAll():
    global btnS, btnM, btn1, btn2, cTimeOpt
    btnS["state"] = DISABLED
    btnM["state"] = DISABLED
    btn1["state"] = DISABLED
    btn2["state"] = DISABLED
    cTimeOpt["state"] = DISABLED

def enableAll():
    global btnS, btnM, btn1, btn2, cTimeOpt
    btnS["state"] = NORMAL
    btnM["state"] = NORMAL
    btn1["state"] = NORMAL
    btn2["state"] = NORMAL
    cTimeOpt["state"] = NORMAL

# End of GUI part

def convertTS2MP4(overwrite):
    global tsPath, mpPath, tsOpt
    tsOpt = timestampOpt.get()
    if (tsPath == "" or mpPath == ""):
        enableAll()
        return
    saveIni()
    procCount = 0
    skipCount = 0
    errCount = 0
    tsFiles = glob.glob(os.path.join(tsPath, "*.ts"))

    for tsf in tsFiles:
        mpf = os.path.join(mpPath, os.path.splitext(os.path.basename(tsf))[0]+".mp4")
        skip = False
        if (not overwrite):
            if (os.path.isfile(mpf)):
                skip = True
        if (skip):
            skipCount += 1
        else:
            logMsg("Processing: "+tsf)
            cmd = ["ffmpeg",
                   "-y",            # overwrite yes
                   "-i",            # input file, ts file name
                   tsf,
                   "-vcodec",       # video codec:copy
                   "copy",
                   "-tag:v",        # this is for macOS
                   "hvc1",
                   "-acodec",       # audio codec:copy
                   "copy",
                   mpf]             # output file, mp4 file name
            res = subprocess.run(cmd, stderr=subprocess.PIPE)
            if (res.returncode == 0):
                procCount += 1
                if tsOpt:
                    ftime = os.stat(tsf)
                    os.utime(path=mpf, times=(ftime.st_atime, ftime.st_mtime))
            else:
                errCount += 1
#                print(res.stderr)
                logMsg("stderr:"+res.stderr.decode('utf-8'))
    
#        logMsg(tsf)
#        logMsg(mpf)

    logMsg("Processed: "+str(procCount)+" file(s) / Skipped: "+str(skipCount)+" file(s) / Error: "+str(errCount)+" files(s)")
    #thread.join()
    enableAll()

def loadIni():
    global tsPath, mpPath, iniFile, tsOpt
    from os.path import expanduser
    home = expanduser("~")
    iniFile = os.path.join(home, 'ts2mp4.ini')
    logMsg("ini file: " + iniFile)

    try:
        tree = ET.parse(iniFile)
        root = tree.getroot()

        for item in root:
            name = item.attrib["name"]
            value = item.attrib["value"]
            if name == "tsPath":
                tsPath = value
            if name == "mpPath":
                mpPath = value
            if name == "tsOpt":
                tsOpt = (value == "1")
    except:
        tsPath = ""
        mpPath = ""
        tsOpt = TRUE


def saveIni():
    global tsPath, mpPath, iniFile, tsOpt

    if tsPath != "" and mpPath != "":
        root = ET.Element("data")
        item1 = ET.SubElement(root, "item")
        item1.set("name", "tsPath")
        item1.set("value", tsPath)
        item2 = ET.SubElement(root, "item")
        item2.set("name", "mpPath")
        item2.set("value", mpPath)
        item3 = ET.SubElement(root, "item")
        item3.set("name", "tsOpt")
        item3.set("value", "1" if (tsOpt) else "0")
        tree = ET.ElementTree(root)
        tree.write(iniFile, encoding="utf-8")

if __name__ == "__main__":
    main()
