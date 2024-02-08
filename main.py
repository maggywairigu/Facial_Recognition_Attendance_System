import pickle
from datetime import datetime

import cv2
import os
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://attendance-system-ab9c9-default-rtdb.firebaseio.com/",
    "storageBucket": "attendance-system-ab9c9.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

""" 
importing the mode images into a list
"""
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

"""
Load the encoding file
"""
print("Loading Encoding File ...")
file = open("EncodeFile.p", "rb")
encodeListKnowWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnowWithIds
print(studentIds)
print("Encode File Loaded")

modeType = 0
counter = 0
imgStudent = []

while True:
    success, img = cap.read()

    imgSmall = cv2.resize(img, (0,0),None,0.25, 0.25)
    imgSmall = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    faceCurrentFrame = face_recognition.face_locations(imgSmall)
    encodeCurrentFrame = face_recognition.face_encodings(imgSmall, faceCurrentFrame)

    imgBackground[162:162+480, 55:55+640] = img
    imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]

    for encodeFace, faceLocation in zip(encodeCurrentFrame, faceCurrentFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDistance = face_recognition.face_distance(encodeListKnown, encodeFace)
        #print("matches: ", matches)
        #print("Face Distance: ", faceDistance)

        matchIndex = np.argmin(faceDistance)
        #print("Match Index", matchIndex)

        if matches[matchIndex]:
            #print("Known face detected")
            #print(studentIds[matchIndex])
            y1, x1, y2, x2 = faceLocation
            y1, x1, y2, x2 = y1*4, x1*4, y2*4, x2*4
            bbox = 55+x1, 162+y1, x2-x1, y2-y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

            id = studentIds[matchIndex]
            if counter == 0:
                counter = 1
                modeType = 1

    if counter != 0:
        if counter == 1:
            """Get the data"""
            studentInfo = db.reference(f'Users/{id}').get()
            print(studentInfo)

            """Get the image from storage"""
            blob = bucket.get_blob(f'Images/{id}.png')
            array = np.frombuffer(blob.download_as_string(), np.uint8)
            imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

            """Update data of the attendance"""
            datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")

            secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
            print(secondsElapsed)

            ref = db.reference(f'Users/{id}')
            studentInfo['total_attendance'] += 1
            ref.child('total_attendance').set(studentInfo['total_attendance'])

        if 10<counter<20:
            modeType = 2

        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        if counter <= 10:
            cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 1)
            cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(imgBackground, str(id), (1006, 493),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
            cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
            cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
            (w,h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX,1 ,1)
            offset = (414-w)//2
            cv2.putText(imgBackground, str(studentInfo['name']), (808+offset, 445),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

            imgBackground[175:175+216, 909:909+216] = imgStudent
            counter += 1

        if counter>=20:
            counter = 0
            modeType = 0
            studentInfo = []
            imgStudent = []
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]


    cv2.imshow("Webcam Interface", imgBackground)
    cv2.waitKey(1)