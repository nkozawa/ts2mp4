# ts2mp4 - Convert HDZERO Goggle DVR files in TS format to MP4 files
# Author: KozakFPV  
# Copyright (C) 2024 by Nobumichi Kozawa

version = "0.0"

from tkinter import *
from tkinter import filedialog
from tkinter import ttk
#from tkinter import messagebox
import os
#import datetime
import xml.etree.ElementTree as ET
#import atexit

root = Tk()
frame = ttk.Frame(root, padding=10)
fMsg = ttk.Frame(frame, padding=10)
txtMsg = Text(fMsg, height=15, width=80)

rbVar = StringVar()

inputPath = StringVar()
outputPath = StringVar()

def main():
    loadIni()
    inputPath.set(tsPath)
    outputPath.set(mpPath)
    style = ttk.Style()
# comment out following line because 'alt' does not work with MacOS Venture and works with default theme well
    style.theme_use('alt')  # to avoid MacOS Dark mode issue with default ttk thema 'aqua'
    root.title('ts2mp4')
    frame.pack()

    fTS = ttk.Frame(frame)
    fTS.pack(anchor=W)
    btn = ttk.Button(
        fTS, text='HDZERO MicroSD Path(TS files)', width=30,
        command=bTSGetPath)
    btn.pack(side=LEFT)
    eIN = ttk.Entry(fTS, textvariable=inputPath, state='readonly', width=30)
    eIN.pack(side=LEFT)
    
    fMP = ttk.Frame(frame)
    fMP.pack(anchor=W)
    btn = ttk.Button(
        fMP, text='Output path(MP4 files)', width=30,
        command=bMPGetPath)
    btn.pack(side=LEFT)
    eOUT = ttk.Entry(fMP, textvariable=outputPath, state='readonly', width=30)
    eOUT.pack(side=LEFT)

    fDO = ttk.Frame(frame)
    fDO.pack(anchor=W)
    btn1 = ttk.Button(
        fDO, text='Start, no overwrite', width=25,
        command=bStart)
    btn1.pack(side=LEFT)
    btn2 = ttk.Button(
        fDO, text='Start, overwrite all', width=25,
        command=bStart)
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
    global tsPath, mpPath
    #print(opt)
    saveIni()

def logMsg(msg):
    txtMsg.insert(END, msg+"\n")
    txtMsg.see(END)

# End of GUI part

def loadIni():
    print("<<<")
    global tsPath, mpPath, iniFile
    from os.path import expanduser
    home = expanduser("~")
    iniFile = os.path.join(home, 'ts2mp4.ini')
    logMsg("ini file: " + iniFile)

    try:
        tree = ET.parse(iniFile)
        root = tree.getroot()

        for item in root:
            name = item.attrib["name"]
            path = item.attrib["path"]
            print(name+","+path)
            if name == "tsPath":
                tsPath = path
            if name == "mpPath":
                mpPath = path
    except FileNotFoundError as e:
        tsPath = ""
        mpPath = ""

    print(tsPath+","+mpPath)


def saveIni():
    global tsPath, mpPath, iniFile
    print(">>>")

    if tsPath != "" and mpPath != "":
        print("...")
        root = ET.Element("data")
        item1 = ET.SubElement(root, "item")
        item1.set("name", "tsPath")
        item1.set("path", tsPath)
        item2 = ET.SubElement(root, "item")
        item2.set("name", "mpPath")
        item2.set("path", mpPath)
        tree = ET.ElementTree(root)
        tree.write(iniFile, encoding="utf-8")

if __name__ == "__main__":
    main()