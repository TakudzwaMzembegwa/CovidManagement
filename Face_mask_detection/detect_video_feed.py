from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import VideoStream
import numpy as np
import requests
import imutils
import json
import time
import cv2
import os

BUILDING = "uwc-cams-lab-c"
DESK = "C5"

pc_free = False
wearing_mask = True
last_wearing_mask = time.time()
last_use = time.time()


def get_user():
    responce = requests.get(
        f"https://covid-management-api.herokuapp.com/useratdesk/{DESK}")
    user = json.loads(responce.text)
    if(len(user) == 0):
        return {}
    return user[0]


def update_user(wearing_mask, desk):
    user = get_user()
    # If the is no user using the desk don`t make any updates
    if(len(user) == 0):
        return
    form = {"studentNumber": user["id"] , "mask": wearing_mask, "desk": desk}
    print("user", form)
    responce = requests.post("https://covid-management-api.herokuapp.com/userstatus", data=form)
    print(responce)


def update_desk(state):
    form = {"building": BUILDING, "desk": DESK, "state": state}
    print("update desk")
    requests.post(
        "https://covid-management-api.herokuapp.com/building", data=form)


def detect(frame, faceNet, maskNet):
    global last_use, pc_free
    # frame dimensions
    (height, width) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300),
                                 (104.0, 177.0, 123.0))

    # Getting face detections rom the Net
    faceNet.setInput(blob)
    detections = faceNet.forward()

    faces = []
    locations = []
    predictions = []

    for i in range(0, detections.shape[2]):
        # get the confidence[0-1] of the detection
        confidence = detections[0, 0, i, 2]

        # remove detections with low confidence
        if confidence > 0.7:
            # compute the (x, y)-coordinates "bounding" the face
            box = detections[0, 0, i, 3:7] * \
                np.array([width, height, width, height])
            (startX, startY, endX, endY) = box.astype("int")

            # ensure the bound is within the frame
            (startX, startY) = (max(0, startX), max(0, startY))
            (endX, endY) = (min(width - 1, endX), min(height - 1, endY))

            # extract and formarting the face
            face = frame[startY:endY, startX:endX]
            if face.any():
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                face = cv2.resize(face, (224, 224))
                face = img_to_array(face)
                face = preprocess_input(face)

                faces.append(face)
                locations.append((startX, startY, endX, endY))

    now = time.time()
    # only predict if one or more faces are detected
    if len(faces) > 0:
        # making batch predictions on all detected faces
        faces = np.array(faces, dtype="float32")
        predictions = maskNet.predict(faces, batch_size=32)
        last_use = time.time()
        pc_free = False
    # Set the desk free if has not been used for more than 10 mins
    # And also remove it from the last user`s data`
    elif((now - last_use) > 20 and not pc_free):
        update_user("YES", "")
        update_desk("FREE")
        pc_free = True

    # return tuple of the face locations and their corresponding predictions
    return (locations, predictions)


def exe():
    # iterate over video stream frames
    while True:
        global last_wearing_mask, wearing_mask
        # Get the frame and resize it to a max width of 400 pixels
        frame = vs.read()
        frame = imutils.resize(frame, width=400)

        # detect faces and make predictions (mask or no_mask)
        (locations, predictions) = detect(frame, faceNet, maskNet)

        # loop over the detected faces
        for (box, pred) in zip(locations, predictions):
            # Face bounding box
            (startX, startY, endX, endY) = box
            # Prediction
            (mask, withoutMask) = pred

            label = ""
            # determine the class label
            if mask > withoutMask:
                label = "Mask"
                last_wearing_mask = time.time()
                # If the user was not wearing a mask, update their status
                if(not wearing_mask):
                    wearing_mask = True
                    update_user("YES", DESK)
            else:
                label = "No Mask"
                # If there user has not been wearing a mask for more than 10 sec update their status
                now = time.time()
                if((now - last_wearing_mask) > 10 and wearing_mask):
                    update_user("NO", DESK)
                    wearing_mask = False
            # colour of face frame
            color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

            # include the probability in the label
            label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

            # display the label and bounding box
            cv2.putText(frame, label, (startX, startY - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

        # show the output frame on the video stream
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # Quit if `q` is pressed
        if key == ord("q"):
            break


if __name__ == "__main__":
    # loading the serialized face detector
    print("[INFO] Loading face detector model...")
    faceNet = cv2.dnn.readNet(
        "deploy.prototxt", "res10_300x300_ssd_iter_140000.caffemodel")

    # loading the face mask detector model
    print("[INFO] Loading face mask detector model...")
    maskNet = load_model("keras_model.h5")

    # initialize the video stream and allow the camera sensor to warm up
    print("[INFO] Starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(2.0)

    exe()

    cv2.destroyAllWindows()
    vs.stop()
