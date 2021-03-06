# USAGE
# python real_time_object_detection.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel --config eagleye_conf

import os
import push_to_db
#sys.path.append(os.getcwd())
# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
from datetime import datetime
from collections import Counter
from itertools import takewhile
import producer
from multiprocessing import Process, Pool
import logging
from logging.handlers import RotatingFileHandler
import sys

log_file_path=os.path.join("/var", "log")
log_file="eagle_eye.log"
logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(os.path.join(log_file_path,log_file),
    maxBytes=50000000,backupCount=5)
logger.addHandler(handler)

DATABASE = os.path.join(os.getcwd(), '..', 'db.sqlite3')

# send the database to kafka producer
Process(target = producer.main, kwargs={"DATABASE" : DATABASE}).start()
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
                help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
                help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.3,
                help="minimum probability to filter weak detections")
ap.add_argument("-f", "--config", default="eagleye_conf",
                help="The configuration file will contain the a dictionary"\
                " of <room number> and <camera IP> pair.")
ap.add_argument("-d", "--debug", action="store_true",
                help="For debugging")
args = vars(ap.parse_args())

# read from conf file
config = args["config"]
_conf = __import__(config)

try:
    MAX_PROCESSES = _conf.MAX_PROCESSES
except AttributeError as _ae:
    logger.info("MAX_PROCESSES not found in conf file. Defaulting to 2.")
    MAX_PROCESSES = 2

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
logger.info("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

def detect(ip, room_no):
        # initialize the video stream, allow the cammera sensor to warmup,
        # and initialize the FPS counter
        logger.info("====[INFO] starting video stream for %s====" %ip)
        vs = VideoStream(src=ip).start()
        time.sleep(2)
        #time.sleep(1)
        fps = FPS().start()

        # loop over the frames from the video stream
#        while True:
        #count = 0
        #while count in range(0, 10):
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
        t1 = datetime.now()
        frame = vs.read()
        frame = imutils.resize(frame, width=400)

        # grab the frame dimensions and convert it to a blob
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                     0.007843, (300, 300), 127.5)

        # pass the blob through the network and obtain the detections and
        # predictions
        net.setInput(blob)
        detections = net.forward()
        # print "here are the detections"
        # print detections
        # print "here are the np.arrange"
        # print np.arange(0, detections.shape[2])
        # print "confidence"
        # for i in np.arange(0, detections.shape[2]):
        #    print detections[0, 0, i, 2]
        # time.sleep(2000)
        person_count = 0
        # loop over the detections
        for i in np.arange(0, detections.shape[2]):

            # extract the confidence (i.e., probability) associated with
            # the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > args["confidence"]:
                # extract the index of the class label from the
                # `detections`, then compute the (x, y)-coordinates of
                # the bounding box for the object
                idx = int(detections[0, 0, i, 1])
                if CLASSES[idx] == "person":
                    person_count += 1
                # if idx != 15:
                #    break
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                # draw the prediction on the frame
                    label = "{}: {:.2f}%".format(CLASSES[idx],
                                             confidence * 100)
                    cv2.rectangle(frame, (startX, startY), (endX, endY),
                              COLORS[idx], 2)
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(frame, label, (startX, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
            logger.info("Number of people detected in %s: %s" %(ip, person_count))

            p_queue = push_to_db.Queue()
            p_queue.enqueue(person_count)

            if p_queue.size() == 30:
                p_queue.dequeue()
                freq = Counter(p_queue)
                mostfreq = freq.most_common()
                mode = list(takewhile(lambda _x : _x[1] == mostfreq[0][1],mostfreq))
                max_mode = mode[-1][0]

            else:
                max_mode = person_count

            #logger.info("Pushing into database: %s" % DATABASE)
            db = push_to_db.Db(DATABASE)
            #logger.info("Updating the database: %s" % DATABASE)
            db.update(room_no, max_mode)
            # db.select()
            if args["debug"]:
                cv2.imshow("Frame", frame)
                #key = cv2.waitKey(1) & 0xFF

            time.sleep(1.5)
            t2 = datetime.now()
            #logger.info('Frame processing time: ', (t2 - t1))
            # if the `q` key was pressed, break from the loop
            #if key == ord("q"):
            #    break

            # update the FPS counter
            fps.update()
            #count += 1

        # stop the timer and display FPS information
        fps.stop()
        #logger.info("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
        #logger.info("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

        # do a bit of cleanup
        cv2.destroyAllWindows()
        vs.stop()
        logger.info("====END OF FUNCTION====: %s" %ip)

if __name__ == "__main__":
    pool = Pool(processes=MAX_PROCESSES)
    while True:
        results = [pool.apply_async(detect, (_conf.ips[key], key)) for key in _conf.ips]
