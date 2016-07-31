import sys
#ros also has cv2, ignore it
rosPath = '/opt/ros/kinetic/lib/python2.7/dist-packages';
if rosPath in sys.path:
    sys.path.remove(rosPath);
import cv2  
import time
import os
import fcntl

def addFileName(name):
    newlist = open('/RAM1/avi/newlist','a')
    fcntl.flock(newlist.fileno(),fcntl.LOCK_EX) 
    newlist.write(name + '\n')
    newlist.close()

cameraCapture = cv2.VideoCapture(0)  
fps = 5 # an assumption  
size = (int(cameraCapture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)),int(cameraCapture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)))  
fname = time.strftime('%F-%H-%M-%S') + '.avi';
videoWriter = cv2.VideoWriter('/RAM1/avi/%s'%fname, cv2.cv.CV_FOURCC('M','J','P','G'), fps, size)  
num = 0
try:
    while True:  
        success, frame = cameraCapture.read()  
        if success:
            num+=1
            videoWriter.write(frame)  
        if num%50 == 0:
            videoWriter.release()
            addFileName(fname)
            fname = time.strftime('%F-%H-%M-%S') + '.avi';
            videoWriter = cv2.VideoWriter('/RAM1/avi/%s'%fname, cv2.cv.CV_FOURCC('M','J','P','G'), fps, size)  
except:
    addFileName(fname)
