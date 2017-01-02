#!/usr/bin/env python
import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

NODE_NAME = "object_detection_node"
SUB_TOPIC = "image"
PUB_TOPIC = ""
QUEUE_SIZE = 10

waitValue = 1

cv2.namedWindow("original")
cv2.moveWindow("original", 10,50)
cv2.namedWindow("canny")
cv2.moveWindow("canny",600,50)
#cv2.namedWindow("equ")
#cv2.moveWindow("equ",600,380)


class ObjectDetectionNode:
    def __init__(self, sub_topic, pub_topic):
        self.bridge = CvBridge()

        self.image_sub = rospy.Subscriber(sub_topic, Image, self.callback)
        rospy.spin()

    def callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            rospy.logerr(e)
			
			
	def correct_gamma(image, gamma=1.0):
		# build a lookup table mapping the pixel values [0, 255] to
		# their adjusted gamma values
		invGamma = 1.0 / gamma
		table = np.array([((i / 255.0) ** invGamma) * 255
			for i in np.arange(0, 256)]).astype("uint8")
 
		# apply gamma correction using the lookup table
		return cv2.LUT(image, table)
	
	#copyFrame = cv_image.copy()
	resizedImage = cv2.resize(cv_image.copy(),None,fx=0.5, fy=0.5, interpolation = cv2.INTER_CUBIC)
	
	#cv2.imshow("Image", cv_image)
	#cv2.waitKey(3)
	videoHeight, videoWidth , _ = resizedImage.shape
	copyFrame = np.zeros(resizedImage.shape, np.uint8)
	# NOTE: its img[y: y + h, x: x + w]
	copyFrame[(videoHeight/2) : videoHeight, 0: videoWidth] = resizedImage[(videoHeight/2) : videoHeight, 0: videoWidth] # Crop from x, y, w, h -> 100, 200, 300, 400

	#copyFrame = correct_gamma(copyFrame,0.5)
	#hsv = cv2.cvtColor(resizedImage, cv2.COLOR_BGR2HSV)
	# range of yellow color in HSV
	#lower_color = np.array([23,100,80]) # 15 geht mehr ins orange.. 20 ist noch gelblich
	#upper_color = np.array([45,255,255])
	
	# Threshold the HSV image to get only yellow colors
	#hsvMask = cv2.inRange(hsv, lower_color, upper_color)
	# close small holes
	
	#hsvMask = cv2.morphologyEx(hsvMask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
	#copyFrame = cv2.cvtColor(copyFrame, cv2.COLOR_BGR2GRAY)
	#equ = cv2.equalizeHist(copyFrame)
	
	canny = cv2.Canny(cv2.medianBlur(copyFrame,5),75,36,3)
	
	#canny = cv2.blur(canny, (3,3))
	#canny = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
	# Bitwise-AND mask and original image
	#mask = cv2.bitwise_and(canny, canny, mask= hsvMask)
	
	#versuch alle linien zu uebermalen sodass nur noch der kreis uebrig bleibt,
	#funktioniert nicht wie vorgestellt
	#lines = cv2.HoughLinesP(canny,1,np.pi/180,45,5,2)
	#for line in lines:
	#	for x1,y1,x2,y2 in line:
	#		cv2.line(resizedImage,(x1,y1),(x2,y2),(255,0,0),2)
	#		cv2.line(canny,(x1,y1),(x2,y2),(0,0,0),2)
	
	#find circles in image
	circles = cv2.HoughCircles(canny,cv2.cv.CV_HOUGH_GRADIENT,1, 15, param1=40,param2=25,minRadius=1) ##,maxRadius=100)
	#res = cv2.cvtColor(res, cv2.COLOR_GRAY2BGR)
	if circles is not None:
		#waitValue = 0
		rMax = 0
		xMax = 0
		yMax = 0
		
	# convert the (x, y) coordinates and radius of the circles to integers
		#circles = np.round(circles[0, :]).astype("int")
		circles = np.uint16(np.around(circles))

	# loop over the (x, y) coordinates and radius of the circles
		for (x, y, r) in circles[0,:]:
	# draw the circle in the output image, then draw a rectangle
	# corresponding to the center of the circle
			posCalc = float(r)/float(y)
			
			if  posCalc < 0.064 and posCalc > 0.049:
				#waitValue = 0
			
				cv2.circle(resizedImage, (x, y), r, (0, 255, 0), 4)
				cv2.putText(resizedImage, str(r), (x,y), cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,0,0),2)
				cv2.putText(resizedImage, str(x) + " " + str(y), (x,y+10), cv2.FONT_HERSHEY_SIMPLEX,0.4,(5,0,200),1)
				#look for the biggest circle
				if r > rMax:
					rMax = r
					xMax = x
					yMax = y
		#southPoint = int(yMax+(rMax))            
		#cv2.circle(resizedImage, (xMax, yMax), rMax, (0, 0, 255), 2)
		
		#cv2.circle(videoFrame, (xMax, southPoint),1, (255,0,0),2)
		#print("Distance: " + str(videoHeight-southPoint) + " in pixel")


	
	#cv2.putText(videoFrame, str(frameIdx), (100,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
	
	cv2.imshow("original", resizedImage)
	cv2.imshow("canny", canny)
	#cv2.imshow("equ",canny)
		   
	#cv2.imshow("result", res)
	
	key = cv2.waitKey(waitValue)
        
	## if key & 0xFF == ord('p'):
		## if(waitValue == 0):
			## waitValue = 10
		## else:
			## waitValue = 0
	## if key & 0xFF == ord('q'):
		## print("q pressed")
	

def main():
    # Initialisiere den Knoten
    rospy.init_node(NODE_NAME, anonymous=True)
    try:
        ObjectDetectionNode(SUB_TOPIC, PUB_TOPIC)
    except KeyboardInterrupt:
        rospy.loginfo("Shutting down node %s", NODE_NAME)

if __name__ == '__main__':
    main()
