# By: Aaron Cayabyab, Jagmeet Cheema, Kabir Sangha
# SET UP
# Luminance: (accuracy maP = 74.3%)
# A software that detects Burglars in low-light conditions. Two alarms integrated into the system that allows
# for SMS alert and Sound alert. The system gets frames from a video stream and pre-processes the frame through means of
# gamma correction and histogram equalization. The frames are then fed into a network that detects 'persons' in the frame,
# creating a bounding box. This network uses a trained model based on the PASCAL VOC0712 dataset. It has a mAP of 74.3%.
# After a few 'ticks', the alarms will trigger if the burglar is still within the frame.

# Import required packages
import sys
import os
import tkinter as tk
from tkinter import ttk
from tkinter import *
from PIL import ImageTk 
from PIL import Image

#Initialize GUI
root = tk.Tk()
root.configure(bg='black')
root.title("Luminance")
frame = tk.Frame(master=root, width=800, height=400, bg='black')
bottom = Frame(root)
frame.pack()
bottom.pack(side=BOTTOM)

#Initialization variables
sms= False
alert = False

def run():
	if sms and alert: #All are enabled
		os.system('python RealTimeDetector.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel --alert True --sound True')
	elif sms and alert==False: #SMS enabled
		os.system('python RealTimeDetector.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel --alert True')
	elif alert and sms==False: #Sound alarm enabled
		os.system('python RealTimeDetector.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel --sound True')
	else: #All disabled
		os.system('python RealTimeDetector.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel')
	print(sms)

def toggleSMS():
	global sms
	if sms==True:
		smsLabel.configure(text="SMS -> OFF")
		sms = False
	else:
		smsLabel.configure(text="SMS -> ON")
		sms = True

def toggleAlert():
	global alert
	if alert==True:
		alarmLabel.configure(text="ALARM -> OFF")
		alert = False
	else:
		alarmLabel.configure(text="ALARM -> ON")
		alert = True
	
#GUI Labels and Buttons
codeLabel = Label(frame, text='        XF02        ', bg ='black', fg="yellow", font=("Helvetica", 16))
codeLabel.pack()
projectLabel = Label(frame, text='        Burglar Detection In The Dark        ', bg='black', fg="yellow", font="Times 24 bold")
projectLabel.pack()
titleLabel = Label(frame, text='        Luminance        ', bg='black', fg="yellow", font="Times 48 bold italic")
titleLabel.pack()
authorLabel = Label(frame, text='        Aaron, Jagmeet, Kabir        ', bg ='black', fg="white", font=("Helvetica", 14))
authorLabel.pack()

#Image
img = ImageTk.PhotoImage(Image.open("Resources/Burglar in the dark.jpg"))
imglabel = Label(root, image=img)
imglabel.pack(padx=1,pady=1)

#Button to run program
button1 = Button(frame, text='Run the program',bg="black", command=run)
button1.pack(padx=1, pady=5)

#SMS and Alarm Labels and Buttons
smsLabel = Label(frame, text="SMS -> OFF", bg ='blue', fg="white")
smsLabel.pack(padx=1, pady=5, )
alarmLabel = Label(frame, text="ALARM -> OFF", bg ='red',fg="white")
alarmLabel.pack(padx=5, pady=5)

smsToggleBtn = Button(bottom, text='SMS', bg="black", command=toggleSMS)
smsToggleBtn.pack(padx=10, side=LEFT)
alertToggleBtn = Button(bottom, text='Alarm', command=toggleAlert)
alertToggleBtn.pack(padx=10, side=LEFT)

#Destroy window
root.bind("<q>", lambda e: root.destroy())

#Run loop
root.mainloop()
