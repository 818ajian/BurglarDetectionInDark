# By: Aaron Cayabyab, Jagmeet Cheema, Kabir Sangha
# RUN TIME
# Luminance: (accuracy maP = 74.3%)
# A software that detects Burglars in low-light conditions. Two alarms integrated into the system that allows
# for SMS alert and Sound alert. The system gets frames from a video stream and pre-processes the frame through means of
# gamma correction and histogram equalization. The frames are then fed into a network that detects 'persons' in the frame,
# creating a bounding box. This network uses a trained model based on the PASCAL VOC0712 dataset. It has a mAP of 74.3%.
# After a few 'ticks', the alarms will trigger if the burglar is still within the frame.

# Import required packages
from imutils.video import VideoStream
from imutils.video import FPS
from twilio.rest import Client
from playsound import playsound
import numpy as np
import argparse
import imutils
import time
import cv2
import math
import datetime

#twilio account setup
account_sid = ""
auth_token = ""
client = Client(account_sid, auth_token)

#Counters
frameCounter = 0
twilioCount = 0
alarmCount = 0

# Alarm System variables
isTwilioStarted = True 
isMessageSent = True

#Trackbar Initial variables
isAlarmOn = 0
isSMSOn = 0


##Send Twilio SMS Message
def sendSMS():
	print("Message sent")
	message = client.messages.create(
		to="",
		from_="",
		body="INTRUDER ALERT!")

##Gamma Correction Function - Returns gamma corrected frame
def adjustGamma(frame, gamma= 1.5):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")

	# apply gamma correction using the lookup table
	return cv2.LUT(frame, table)

##Display current time
def displayTime():
	now = datetime.datetime.now()
	nowString = (now.strftime("%Y-%m-%d %H:%M:%S"))
	cv2.putText(gammaFrame, nowString, (20, 320),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, True)

##Trackbar callback function
def nothing(x):
	pass

##Calculates PSNR b/w first frames
def psnr(img1, img2):
    mse = np.mean( (img1 - img2) ** 2 )
    if mse == 0:
    	return 100
    PIXEL_MAX = 255.0
    return 20 * math.log10(PIXEL_MAX / math.sqrt(mse))


# Initialize argument parsing
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
	help="minimum probability to filter weak detections")
ap.add_argument("-a", "--alert", type=bool, default=False,
	help="toggle Twilio SMS alert, default = false")
ap.add_argument("-s", "--sound", type=bool, default=False,
	help="toggle Sound alert, default = false")
args = vars(ap.parse_args())

# Initialize MobileNet SSD class labels from model
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]

# Random color for detection bounding box
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# Load trained model
print("INFO: Model loading")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# Initialize video stream and FPS counte
print("INFO: Video stream starting")
vs = VideoStream(src=0).start()
time.sleep(2.0)
fps = FPS().start()

# Loop over video stream frames
while True:
	# Grab frame from threaded video stream and resize
	frame = vs.read()
	frame = imutils.resize(frame, width=600)
	frameOrig = frame

	#PSNR check for first two frames
	if frameCounter < 2:
		if frameCounter == 0:
			frame1 = vs.read()
		elif frameCounter == 1:
			frame2 = vs.read()
		frameCounter += 1

#Alarm System Initialization
	#Alarm System 1: SMS send after 100 ticks
	if (twilioCount > 100 and isMessageSent == False and isTwilioStarted == False and args["alert"] == True):
		sendSMS()
		isTwilioStarted = True
		isMessageSent = True
	
	#Alarm System 2: Sound after 50 ticks
	if(alarmCount > 50 and args["sound"] == True):
		playsound('Resources/Alarm.wav', False)
		alarmCount = 0

#Video Preprocessing Block -- if denoise argument true, process non-local means denoising 
	#Histogram Equalization
	yuvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
	yuvFrame[:, :, 0] = cv2.equalizeHist(yuvFrame[:, :, 0])
	resultHistEq = cv2.cvtColor(yuvFrame, cv2.COLOR_YUV2BGR)
	#Gamma Correction
	gammaFrame = adjustGamma(resultHistEq, 1.5) 

#Deep Learning and Object Detection Block -- Send frame to object detection network
	# Grab frame dimensions and convert to blob
	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(cv2.resize(resultHistEq, (300, 300)),
		0.007843, (300, 300), 127.5)

	# Feed blob to network get predictions
	net.setInput(blob)
	detections = net.forward()

	# Loop over detections
	for i in np.arange(0, detections.shape[2]):
		# Extract confidence associated with prediction
		confidence = detections[0, 0, i, 2]

		# Filter out detections by confidence value initialized (0.2)
		if confidence > args["confidence"]:

			# extract the index of the class label from the
			# `detections`, if not "person" ignore, 
			# else compute bounding box coordinates
			idx = int(detections[0, 0, i, 1])
			if CLASSES[idx] != "person":
				continue
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")


			# Draw prediction on frame
			label = "{}: {:.2f}%".format("Burglar", confidence * 100)
			cv2.rectangle(gammaFrame, (startX, startY), (endX, endY), COLORS[idx], 4)
			y = startY - 15 if startY - 15 > 15 else startY + 15
			cv2.putText(gammaFrame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
			
			#Increment alarm ticks
			twilioCount += 1
			alarmCount += 1
					
	#Display time
	displayTime()
	#Display output frames
	title = "Luminance"
	twoFrames = np.hstack((frameOrig, gammaFrame))
	cv2.imshow(title, twoFrames)
	
#Run-Time GUI: Enable/Disable alarm systems
	if(args["sound"] == True):
		cv2.createTrackbar("Toggle Sound", title, 0, 1, nothing)
	if(args["alert"] == True):
		cv2.createTrackbar("Toggle SMS", title, 0, 1, nothing)
	
	isAlarmOn = cv2.getTrackbarPos("Toggle Sound", title)
	isSMSOn = cv2.getTrackbarPos("Toggle SMS", title)
	
	if(isAlarmOn == 1):
		args["sound"] = True
	else:
		alarmCount = 0
		args["sound"] = False

	if(isSMSOn == 1):
		isTwilioStarted = False

		if(twilioCount > 120 and isMessageSent == True and isTwilioStarted == False):
			cv2.setTrackbarPos("Toggle SMS", title, 0)
	else:
		isTwilioStarted = True
		isMessageSent = False
		twilioCount = 0

	#If 'q' pressed, break from loop
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break

	#Update FPS Counter
	fps.update()

#Stop timer and display FPS
fps.stop()

#Compute PSNR
d=psnr(frame1,frame2)
print("INFO: elapsed time: {:.2f}".format(fps.elapsed()))
print("INFO: approx. FPS: {:.2f}".format(fps.fps()))

print("INFO: PSNR: {:.2f}".format(d))
print("INFO: Detection Count: {:}".format(twilioCount))
print("INFO: Alarm Count: {:}".format(alarmCount))

#Cleanup
cv2.destroyAllWindows()
vs.stop()
