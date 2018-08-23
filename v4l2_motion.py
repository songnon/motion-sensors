#!/usr/bin/env python

"""
motion-track  written by Claude Pageau pageauc@gmail.com
Windows, Unix, Raspberry (Pi) - python opencv2 motion tracking
using web camera or raspberry pi camera module.

This is a python opencv2 motion tracking demonstration program.
It will detect motion in the field of view and use opencv to calculate the
largest contour and return its x,y coordinate.  I will be using this for
a simple RPI robotics project, but thought the code would be useful for
other users as a starting point for a project.  I did quite a bit of
searching on the internet, github, etc but could not find a similar
implementation that returns x,y coordinates of the most dominate moving
object in the frame.  Some of this code is base on a YouTube tutorial by
Kyle Hounslow using C here https://www.youtube.com/watch?v=X6rPdRZzgjg

Here is a my YouTube video demonstrating this demo program using a
Raspberry Pi B2 https://youtu.be/09JS7twPBsQ

This will run on a Windows, Unix OS using a Web Cam or a Raspberry Pi
using a Web Cam or RPI camera module installed and configured

To do a quick install On Raspbian or Debbian Copy and paste command below
into a terminal sesssion to download and install motion_track demo.
Program will be installed to ~/motion-track-demo folder

curl -L https://raw.github.com/pageauc/motion-track/master/motion-track-install.sh | bash

To Run Demo

    cd ~/motion-track-demo
    ./motion-track.py

To Edit settings

   nano config.py

ctrl-x y to save changes and exit.

"""

# import the necessary packages
import logging
import time
import os
import sys
from threading import Thread
import cv2

WEBCAM_HFLIP = True   # default = False USB Webcam flip image horizontally
WEBCAM_VFLIP = False

MIN_AREA = 200 * 3      # excludes all contours less than or equal to this Area
THRESHOLD_SENSITIVITY = 25
BLUR_SIZE = 10
IMAGE_W = 320 * 3
IMAGE_H = 240 * 3

LINE_THICKNESS = 2
# Color data for OpenCV lines and text
CV_WHITE = (255, 255, 255)
CV_BLACK = (0, 0, 0)
CV_BLUE = (255, 0, 0)
CV_GREEN = (0, 255, 0)
CV_RED = (0, 0, 255)
MO_COLOR = CV_RED  # color of motion circle or rectangle

#------------------------------------------------------------------------------
def my_stuff(image_frame, xy_pos):
    """
    This is where You would put code for handling motion event(s)
    Below is just some sample code to indicate area of movement
    I have added image_frame in case you want to save and image
    based on some trigger event. You will need to create
    your own trigger event.  See https://github.com/pageauc/speed-camera
    for tracking moving objects and recording speed images.  There is also
    a security plugin that does not use speed data but just tracks motion
    and records image when trigger length is reached.
    """
    pass

#------------------------------------------------------------------------------
# class WebcamVideoStream:
#     """
#     WebCam initialize then stream and read the first video frame from stream
#     """
#     def __init__(self, cam_src=WEBCAM_SRC, cam_width=WEBCAM_WIDTH,
#                  cam_height=WEBCAM_HEIGHT):
#         self.webcam = cv2.VideoCapture(cam_src)
#         self.webcam.set(3, cam_width)
#         self.webcam.set(4, cam_height)
#         (self.grabbed, self.frame) = self.webcam.read()
#         # initialize the variable used to indicate if the thread should
#         # be stopped
#         self.stopped = False

#     def start(self):
#         """ start the thread to read frames from the video stream """
#         t = Thread(target=self.update, args=())
#         t.daemon = True
#         t.start()
#         return self

#     def update(self):
#         """ keep looping infinitely until the thread is stopped """
#         while True:
#             # if the thread indicator variable is set, stop the thread
#             if self.stopped:
#                 return
#             # otherwise, read the next frame from the webcam stream
#             (self.grabbed, self.frame) = self.webcam.read()

#     def read(self):
#         """ return the frame most recently read """
#         return self.frame

#     def stop(self):
#         """ indicate that the thread should be stopped """
#         self.stopped = True

#------------------------------------------------------------------------------
def track(callback=my_stuff):
    """ Process video stream images and report motion location """
    webcam = cv2.VideoCapture("/dev/video0")
    webcam.set(3, IMAGE_W)
    webcam.set(4, IMAGE_H)
    _, image2 = webcam.read() # initialize image2 to create first grayimage
    image2 = cv2.flip(image2, -1) # flip image
    cv2.imwrite('test.jpg',image2)
    grayimage1 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY) # sRGB
    
    still_scanning = True
    while still_scanning:
        time.sleep(.5)
        # initialize variables
        motion_found = False
        biggest_area = MIN_AREA
        _, image2 = webcam.read()  # grab image
        image2 = cv2.flip(image2, -1) # flip image
        # if WEBCAM:
        #     if WEBCAM_HFLIP and WEBCAM_VFLIP:
        #         image2 = cv2.flip(image2, -1)
        #     elif WEBCAM_HFLIP:
        #         image2 = cv2.flip(image2, 1)
        #     elif WEBCAM_VFLIP:
        #         image2 = cv2.flip(image2, 0)
        grayimage2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        # Get differences between the two greyed images
        difference_image = cv2.absdiff(grayimage1, grayimage2)
        # save grayimage2 to grayimage1 ready for next image2
        grayimage1 = grayimage2
        difference_image = cv2.blur(difference_image, (BLUR_SIZE, BLUR_SIZE))
        # Get threshold of difference image based on
        # THRESHOLD_SENSITIVITY variable
        retval, threshold_image = cv2.threshold(difference_image,
                                                THRESHOLD_SENSITIVITY, 255,
                                                cv2.THRESH_BINARY)
        try:
            contours, hierarchy = cv2.findContours(threshold_image,
                                                   cv2.RETR_EXTERNAL,
                                                   cv2.CHAIN_APPROX_SIMPLE)
        except ValueError:
            threshold_image, contours, hierarchy = cv2.findContours(threshold_image,
                                                                    cv2.RETR_EXTERNAL,
                                                                    cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            # total_contours = len(contours)  # Get total number of contours
            for c in contours:              # find contour with biggest area
                found_area = cv2.contourArea(c)  # get area of next contour
                # find the middle of largest bounding rectangle
                if found_area > biggest_area:
                    motion_found = True
                    biggest_area = found_area
                    (x, y, w, h) = cv2.boundingRect(c)
                    c_xy = (int(x+w/2), int(y+h/2))   # centre of contour
                    r_xy = (x, y) # Top left corner of rectangle
        if motion_found:
            # my_stuff(image2, c_xy) # Do Something here with motion data
            cv2.rectangle(image2, r_xy, (x+w, y+h),
                                      MO_COLOR, LINE_THICKNESS)
            callback(True, image2)
        else:
            callback(False, image2)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    while True:
        """
        Save images to an in-program stream
        Setup video stream on a processor Thread for faster speed
        """
        try:
            logging.info("Initializing USB Web Camera ...")
            vs = WebcamVideoStream().start()
            time.sleep(4.0) # Allow WebCam time to initialize
            track()
        except KeyboardInterrupt:
            vs.stop()
            print("")
            logging.info("User Pressed Keyboard ctrl-c")
            sys.exit(0)