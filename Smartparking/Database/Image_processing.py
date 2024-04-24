import os
import cv2
import numpy as np
import easyocr
import util
from Database.Connect import enter_details

# Define constants
model_cfg_path = os.path.join('.', 'model', 'cfg', 'darknet-yolov3.cfg')
model_weights_path = os.path.join('.', 'model', 'weights', 'model.weights')
input_dir = "C:/Desktop/Hi/"

# Load YOLOv3 model
net = cv2.dnn.readNetFromDarknet(model_cfg_path, model_weights_path)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Choose one image from the input directory
img_name = "Car3.jpg"  # Replace with the actual image file name
img_path = os.path.join(input_dir, img_name)

# Load image
img = cv2.imread(img_path)
H, W, _ = img.shape

# Convert image
blob = cv2.dnn.blobFromImage(img, 1 / 255, (416, 416), (0, 0, 0), True)
net.setInput(blob)

# Get detections
detections = util.get_outputs(net)

# Process detections
bboxes = []
class_ids = []
scores = []
for detection in detections:
    bbox = detection[:4]
    xc, yc, w, h = bbox
    bbox = [int(xc * W), int(yc * H), int(w * W), int(h * H)]
    bbox_confidence = detection[4]
    class_id = np.argmax(detection[5:])
    score = np.amax(detection[5:])
    bboxes.append(bbox)
    class_ids.append(class_id)
    scores.append(score)

# Apply non-max suppression
bboxes, class_ids, scores = util.NMS(bboxes, class_ids, scores)

# Process each detected object
for bbox_, bbox in enumerate(bboxes):
    xc, yc, w, h = bbox
    license_plate = img[int(yc - (h / 2)):int(yc + (h / 2)), int(xc - (w / 2)):int(xc + (w / 2)), :].copy()

    # Threshold license plate image
    license_plate_gray = cv2.cvtColor(license_plate, cv2.COLOR_BGR2GRAY)
    _, license_plate_thresh = cv2.threshold(license_plate_gray, 64, 255, cv2.THRESH_BINARY_INV)

    # Perform OCR
    output = reader.readtext(license_plate_thresh)

    for out in output:
        text_bbox, text, text_score = out
        print("Text:", text)
