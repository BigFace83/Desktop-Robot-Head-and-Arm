
# |B|I|G| |F|A|C|E| |R|O|B|O|T|I|C|S|

#import cv
import time
import cv2
import numpy as np
import sys
import math



DisplayImage = False

print "Starting OpenCV"
capture = cv2.VideoCapture(0)

capture.set(3,384) #1024 640 1280 800 384
capture.set(4,288) #600 480 960 600 288

if DisplayImage is True:
    cv2.namedWindow("camera", 0)
    print ("Creating OpenCV windows")
    cv2.resizeWindow("camera", 320,240) 
    print ("Resizing OpenCV windows")
    cv2.moveWindow("camera", 800,30)
    print ("Moving OpenCV window")
    cv2.waitKey(50)



##################################################################################################
#
# Display Frame - Capture a frame and display it on the screen
#
##################################################################################################
def DisplayFrame():

    ret,img = capture.read()
    ret,img = capture.read()
    ret,img = capture.read()
    ret,img = capture.read()
    ret,img = capture.read() #get a bunch of frames to make sure current frame is the most recent

    cv2.imshow("camera", img)
    cv2.waitKey(20)

    return img


##################################################################################################
#
# Return Frame RGB - Capture a frame and returns an RGB version of the image
#
##################################################################################################
def ReturnFrameRGB():

    ret,img = capture.read()
    ret,img = capture.read()
    ret,img = capture.read()
    ret,img = capture.read()
    ret,img = capture.read() #get a bunch of frames to make sure current frame is the most recent

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return img


##################################################################################################
#
# Save Frame - Capture a frame and display it on the screen
#
##################################################################################################
def SaveFrame(filename):

    ret,img = capture.read()
    ret,img = capture.read()
    ret,img = capture.read()
    ret,img = capture.read()
    ret,img = capture.read() #get a bunch of frames to make sure current frame is the most recent

    cv2.imshow("camera", img)
    cv2.waitKey(20)

    cv2.imwrite(filename,img)

##################################################################################################
#
# FindBall - Grab an image and check for an area of a certain colour dictated by values in 
# ThresholdArray. If nothing found, return -1, else return data about found object
#
##################################################################################################
def FindBall(ThresholdArray):

    BallData = -1
    ret,img = capture.read() #get a bunch of frames to make sure current frame is the most recent
    ret,img = capture.read() 
    ret,img = capture.read()
    ret,img = capture.read()
    ret,img = capture.read() #5 seems to be enough

    imgHSV = cv2.cvtColor(img,cv2.COLOR_BGR2HSV) #convert img to HSV and store result in imgHSVyellow
    lower = np.array([ThresholdArray[0],ThresholdArray[1],ThresholdArray[2]]) #np arrays for upper and lower thresholds
    upper = np.array([ThresholdArray[3], ThresholdArray[4], ThresholdArray[5]])

    imgthreshed = cv2.inRange(imgHSV, lower, upper) #threshold imgHSV
    imgthreshed = cv2.blur(imgthreshed,(3,3))

    img2, contours, hierarchy = cv2.findContours(imgthreshed,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    for x in range (len(contours)):
        contourarea = cv2.contourArea(contours[x])
        if contourarea > 1000:
            rect = cv2.minAreaRect(contours[x])
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(img,[box],0,(0,160,255),1)
 
            boxcentre = rect[0] #get centre coordinates of each object
            boxcentrex = int(boxcentre[0])
            boxcentrey = int(boxcentre[1])
            cv2.circle(img, (boxcentrex, boxcentrey), 5, (0,160,255),-1) #draw a circle at centre point of object
            BallData = [boxcentrex, boxcentrey]
            break
 
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    imgthreshed = cv2.cvtColor(imgthreshed, cv2.COLOR_GRAY2RGB)
 
    return BallData, img, imgthreshed


def destroy():
    
    cv2.destroyAllWindows()
   


