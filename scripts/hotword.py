#!/usr/bin/env python
import rospy
import struct
from std_msgs.msg import String
from kitt.msg import Hotword
# kitt related
import snowboydecoder
import sys
import signal
import os

# define two global flags, 
# one for first level hotword : snowboy
# the other is for second level hotword: start, pause
interrupted = False
paused = False

def interrupt_signal_handler(signal, frame):
    global interrupted
    interrupted = True

def pause_signal_handler(signal, frame):
    print('pause and exit')
    global paused
    paused = True

def interrupt_callback():
    global interrupted
    return interrupted

def pause_callback():
    global paused
    return paused

def second_level_start_callback():
    if not rospy.is_shutdown():
        msg_send.control_msg = 'start'
        pub.publish(msg_send)
        print('start...')

def second_level_pause_callback():
    if not rospy.is_shutdown():
        msg_send.control_msg = 'pause'
        pub.publish(msg_send)
        print('pause...')

def first_level_callback():
    # start the second level detector, if detected
    # publish the ros hotword message
    print('Entering second level detector....')
    global paused
    paused = False
    # define callbacks
    second_level_callbacks = [second_level_start_callback, second_level_pause_callback]
    # Set the signal handler and a 5-second alarm
    signal.signal(signal.SIGALRM, pause_signal_handler)
    signal.alarm(5)
    second_detector.start(detected_callback=second_level_callbacks,
               interrupt_check=pause_callback,
               sleep_time=0.03)

    signal.alarm(0)
    # second_detector.terminate()
    print('Exit Second Level....')
    


def hotword():

    # model files path
    TOP_DIR = os.path.dirname(os.path.abspath(__file__))
    FIRST_RESOURCE_FILE1 = os.path.join(TOP_DIR, "resources/models/snowboy.umdl")
    SECOND_RESOURCE_FILE1 = os.path.join(TOP_DIR, "resources/models/ma_control1.pmdl")
    SECOND_RESOURCE_FILE2 = os.path.join(TOP_DIR, "resources/models/ma_control2.pmdl")
    first_models = FIRST_RESOURCE_FILE1
    second_models = [SECOND_RESOURCE_FILE1, SECOND_RESOURCE_FILE2]

    # capture SIGINT signal, e.g., Ctrl+C
    signal.signal(signal.SIGINT, interrupt_signal_handler)

    # define first level detector
    first_detector = snowboydecoder.HotwordDetector(FIRST_RESOURCE_FILE1, sensitivity=0.5)
    # define second level detector
    sensitivity = [0.5]*len(second_models)
    global second_detector
    second_detector = snowboydecoder.HotwordDetector(second_models, sensitivity=sensitivity)

    #rospy.loginfo(hello_str)

    #start the first level
    
    print('Listening... Press Ctrl+C to exit')
    first_detector.start(detected_callback=first_level_callback,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)
    # Attention: terminate can only be called once
    first_detector.terminate()

if __name__ == '__main__':
    try:

        # define ros node
        pub = rospy.Publisher('hotword', Hotword, queue_size=10)
        rospy.init_node('hotwordNode', anonymous=True)
        msg_send = Hotword()

        hotword()
    except rospy.ROSInterruptException:
        pass