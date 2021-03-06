import argparse
import datetime
import imutils
import time
import cv2
import cv 
import socket
from socket import *
import os
import thread
import RPi.GPIO as GPIO
import random
import sys
import signal
import smtplib
import numpy
#from email.MTMEImage import MIMEImage
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

Motor = 7.5
Bright = 0.5
Msg = ''
file_path = 'image.jpg'
delay = ''
send_mail = ''
num_of_picture = ''
back_setting = ''
On_setting = ''
f_num = 0;
camera = ''
frame = ''
check = 0 # false
text = ''
shoot = ''

###################Signal Handler   #####################
def sinal_handler(signal , frame):
	print "Interrupt!!!!"
        pwm.stop()
	GPIO.cleanup()
	sys.exit(0)
#########################################################


################### GPIO Setting## ###############
GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.OUT) # GREEN
GPIO.setup(15, GPIO.OUT) # RED
GPIO.setup(18, GPIO.OUT) # SERVO
GPIO.setup(23, GPIO.OUT) # BLUE

GPIO.output(15, GPIO.LOW) # RED
GPIO.output(14, GPIO.LOW) # GREEN
GPIO.output(23, GPIO.LOW) # BLUE
pwm = GPIO.PWM(18, 50)
pwm.start(7.5)
##################################################

################### Socket Setting ###############
signal.signal(signal.SIGINT , sinal_handler)
socket = socket(AF_INET , SOCK_STREAM)
socket.setsockopt(SOL_SOCKET , SO_REUSEADDR , 1)

port = 7500


socket.bind(('' , port))
socket.listen(5)

##################################################

############## Message recieve and send image########
# msg fotmat delay/send_mail/num_of_picture/back_setting/On_setting
# Or b+ b0 b- m+ m0 m- BG0 BG1 BG2 BG3 BG4 
def fileSend():
 global client
 global frame
 global Bright
 global Motor
 global num_of_picture
 global back_setting
 global On_setting
 global send_mail
 global camera
 global check
 global text
 global pwm
 global shoot
 sound_file = ""
 string = ""
 GPIO.output(14, GPIO.HIGH) # GREEN
 client , addr = socket.accept()
 print "accept"
 GPIO.output(14, GPIO.LOW) # GREEN
 GPIO.output(15, GPIO.HIGH) # RED
 while True:
  msg = client.recv(1024)
  tuple = msg.split('/')
  print tuple
  delay = tuple[0]

  if msg == '':
   print "User Log out"
   pwm.stop()
   GPIO.output(15, GPIO.LOW) # RED
   thread.start_new_thread(fileSend,())
   back_setting = 0
   return
  if len(tuple) != 1:
   send_mail = tuple[1]
   num_of_picture = tuple[2]
   back_setting = tuple[3]
   On_setting = tuple[4]
   shoot = 'Y'
 
  if delay == 'm+':
    Motor = Motor + 1.0
    #duty = float(Motor) / 10.0 + 2.5
    pwm.ChangeDutyCycle(Motor)
    time.sleep(2)
    print Motor
  elif delay == 'm0':
    Motor = 7.5
    #duty = float(Motor) / 10.0 + 2.5
    pwm.ChangeDutyCycle(Motor)
    time.sleep(2)
    print Motor
  elif delay == 'm-':
    Motor = Motor - 1.0
    #duty = float(Motor) / 10.0 + 2.5
    pwm.ChangeDutyCycle(Motor)
    time.sleep(2)
    print Motor

  elif delay == 'b+':
    Bright = Bright + 0.1
    camera.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, Bright)
    print Bright
  elif delay == 'b0':
    Bright = 0.5
    camera.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, Bright)
    print Bright
  elif delay == 'b-':
    Bright = Bright - 0.1
    camera.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, Bright)
    print Bright

  elif 'BG' in delay and len(delay) == 3:
    back_setting = delay[2]
    print back_setting

  elif On_setting == "1": # Send file to app
    print On_setting
    num = "".join( num_of_picture )
    numi = range(0 , int( num ) )
    for i in numi :
     for i in range( 0 , int(delay)):
      text = str( int(delay) - i)
      check = 1 # true
      time.sleep(1)
      check = 0 # false
     shoot = 'Y'
     time.sleep(1)
     sound_file = str(random.randrange(1,6)) + ".mp3"
     string = "mplayer -vo x11 /home/pi/embeded/" + sound_file
     os.system(string)
     while shoot == 'Y':
       tm = 0
     f = open( file_path , 'r')
     l = f.read()
     while(l):
      client.send(l)
      l = f.read()
     f.close()

  elif On_setting == "0": # Send mail 
    print On_setting
    num = "".join( num_of_picture )
    numi = range(1 , int( num ) )
    for i in range( 0 , int(delay)):
     text = str( int(delay) - i)
     check = 1 # true
     time.sleep(1)
     check = 0 # false
    time.sleep(1)
    sound_file = str(random.randrange(1,6)) + ".mp3"
    string = "mplayer -vo x11 /home/pi/embeded/" + sound_file
    os.system(string)
    while shoot == 'Y':
       tm = 0
    f = open( file_path , 'r')
    l = f.read()
    while(l):
     client.send(l)
     l = f.read()
    f.close()
    MailSend()
    for i in numi :
     for i in range( 0 , int(delay)):
      text = str( int(delay) - i)
      check = 1 # true
      time.sleep(1)
      check = 0 # false
     shoot = 'Y'
     time.sleep(1)
     sound_file = str(random.randrange(1,6)) + ".mp3"
     string = "mplayer -vo x11 /home/pi/embeded/" + sound_file
     os.system(string)
     while shoot == 'Y':
       tm = 0
     MailSend()
  else :
    print 'Error'	
     

#####################################################

############### Mail Send Function ##################

def MailSend():
	global send_mail
	global file_path
	msg = MIMEMultipart()
	msg['Subject'] = 'PhotoBox'
 	
	me = 'woodcook48@gmail.com'
	family = send_mail
	msg['From'] = me
	msg['To'] = send_mail
	msg.preamble = 'PhotoBox mail'
 

	fp = open(file_path, 'rb')
	img = MIMEImage(fp.read())
	fp.close()
	msg.attach(img)
 
	# local server
	#s = smtplib.SMTP('localhost')
	#s.sendmail(me, family, msg.as_string())
	#s.quit()
 
	# another server
	s = smtplib.SMTP_SSL('smtp.gmail.com',465)
	#s.ehlo()
	#s.starttls()
	#s.ehlo()
	s.login("woodcook48","df125qwer!")
	s.sendmail(me, [send_mail], msg.as_string())
	s.quit()

###############################################################

################## Count function #######################

def Count( count ):
 global text
 cnt = range( 0 , count)
 for i in cnt:
  text = str(i)
  check = 1 # true
  time.sleep(1)
  check = 0 # false
#########################################################

################### Image process  ###############
lower_skin = numpy.array([0,59,0])
upper_skin = numpy.array([128,175,255])

camera = cv2.VideoCapture(0)

if camera is None:
 print 'Camera Error\n'
 print 'Program will exit'
 os.exit(0)

thread.start_new_thread(fileSend,())
while( camera.isOpened() ):
 val, frame = camera.read()

 #tmp = camera.get( cv2.cv.CV_CAP_PROP_BRIGHTNESS )
 #print "Bright : " + str(tmp)

 if back_setting == '1' : # Gray
  frame = cv2.cvtColor(frame , cv2.COLOR_BGR2GRAY)

 elif back_setting == '2' : # Flip
  frame = cv2.flip(frame,0)

 elif back_setting == '3' : # Trace
  hsv = cv2.cvtColor(frame , cv2.COLOR_BGR2HSV)
  mask = cv2.inRange(hsv , lower_skin, upper_skin)
  res = frame = cv2.bitwise_and(frame , frame, mask= mask)

 elif back_setting == '4' : # Half
  # generate Gaussian pyramid for A
  G = frame.copy()
  gpA = [G]
  for i in xrange(6):
	G = cv2.pyrDown(G)
	gpA.append(G)

  # generate Gaussian pyramid for B
  G = frame.copy()
  gpB = [G]
  for i in xrange(6):
	G = cv2.pyrDown(G)
	gpB.append(G)


  # generate Laplacian Pyramid for A
  lpA = [gpA[5]]
  for i in xrange(5,0,-1):
	GE = cv2.pyrUp(gpA[i])
	L = cv2.subtract(gpA[i-1],GE)
	lpA.append(L)


  # generate Laplacian Pyramid for B
  lpB = [gpB[5]]
  for i in xrange(5,0,-1):
	GE = cv2.pyrUp(gpB[i])
	L = cv2.subtract(gpB[i-1],GE)
	lpB.append(L)

  # Now add left and right halves of images in each level
  LS = []
  for la,lb in zip(lpA,lpB):
	rows,cols,dpt = la.shape
	ls = numpy.hstack((la[:,0:cols/2], lb[:,cols/2:]))
	LS.append(ls)
  frame = numpy.hstack((frame[:,cols/2:],frame[:,:cols/2]))

 if shoot == 'Y' and check == 0:
  print 'shoot'
  GPIO.output(23, GPIO.HIGH) # BLUE
  cv2.imwrite(file_path, frame)
  GPIO.output(23, GPIO.LOW) # BLUE
  shoot = 'N'
 if check == 1:
  cv2.putText(frame, text, (210, 320), cv2.FONT_HERSHEY_SIMPLEX, 10, (0, 0, 255), 4)
 #cv2.imshow("mask", mask)
 #cv2.imshow("Res", res)
 cv2.imshow("Image", frame)
 key = cv2.waitKey(30)

 if key == ord('q'):
      GPIO.cleanup()
      break

##################################################

socket.close
camera.release()
cv2.destroyAllWindows()