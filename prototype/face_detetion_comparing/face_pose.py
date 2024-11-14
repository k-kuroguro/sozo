import os
import sys

import cv2
import dlib
import numpy as np
from imutils import face_utils

cap = cv2.VideoCapture("../head-pose-face-detection-male.mp4")
detector = cv2.dnn.readNet("./opencv_face_detector_uint8.pb", "./opencv_face_detector.pbtxt")
face_parts_detector = dlib.shape_predictor("shape_predictor_68_face_landmarks_GTX.dat")

from pose_estimator import PoseEstimator

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

pose_estimator = PoseEstimator(frame_width, frame_height)

codec = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter("output.mp4", codec, 60, (frame_width, frame_height))

while True:
    tick = cv2.getTickCount()

    ret, rgb = cap.read()

    if not ret:
        break

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    inputBlob = cv2.dnn.blobFromImage(
        cv2.resize(rgb, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)
    )
    detector.setInput(inputBlob)
    detections = detector.forward()

    # 顔が1つのみ検出された場合にランドマーク検出
    faces = []
    h, w = rgb.shape[:2]
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:  # 信頼度が50%以上の場合に検出
            box = detections[0, 0, i, 3:7] * [w, h, w, h]
            (x, y, x2, y2) = box.astype("int")
            faces.append((x, y, x2 - x, y2 - y))

    if len(faces) == 1:
        x, y, w, h = faces[0]
        cv2.rectangle(rgb, (x, y), (x + w, y + h), (255, 0, 0), 2)

        face = dlib.rectangle(x, y, x + w, y + h)
        face_parts = face_parts_detector(gray, face)
        face_parts = face_utils.shape_to_np(face_parts)

        for i, ((x, y)) in enumerate(face_parts[:]):
            cv2.circle(rgb, (x, y), 1, (0, 255, 0), -1)
            cv2.putText(rgb, str(i), (x + 2, y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)

        face_parts = face_parts.astype(np.float32)

        # Step 3: Try pose estimation with 68 points.
        pose = pose_estimator.solve(face_parts)
        pose_estimator.visualize(rgb, pose, color=(0, 255, 0))

    fps = cv2.getTickFrequency() / (cv2.getTickCount() - tick)
    cv2.putText(
        rgb,
        "FPS:{} ".format(int(fps)),
        (10, 50),
        cv2.FONT_HERSHEY_PLAIN,
        3,
        (0, 0, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.imshow("frame", rgb)
    out.write(rgb)
    if cv2.waitKey(1) == 27:
        break  # esc to quit

out.release()
cap.release()
cv2.destroyAllWindows()
