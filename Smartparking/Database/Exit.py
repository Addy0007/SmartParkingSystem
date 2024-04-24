import os
import cv2
import numpy as np
import easyocr
import util
import time
import socket
from Database.Connect import enter_details
from owncloud import Client


oc = Client('http://192.168.1.16/owncloud')
oc.login('siddhant', 'qwertyuiop')
directory_path = '/testdir/'


def is_directory_empty(directory_path):
    directory_contents = oc.list(directory_path)
    return len(directory_contents) == 0


while is_directory_empty(directory_path):
    print("Directory is empty. Waiting...")
    time.sleep(5)  # Adjust the interval as needed

print("Directory is not empty. Proceeding with the rest of the code.")

# Path to the image file in ownCloud
image_path = '/testdir/entry.png'
destination_dir = os.path.expanduser('~//Downloads')

# Download the image file
oc.get_file(image_path, os.path.join(destination_dir, 'demo.png'))

# Define constants
model_cfg_path = os.path.join('.', 'model', 'cfg', 'darknet-yolov3.cfg')
model_weights_path = os.path.join('.', 'model', 'weights', 'model.weights')
input_dir = destination_dir

# Load YOLOv3 model
net = cv2.dnn.readNetFromDarknet(model_cfg_path, model_weights_path)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Choose one image from the input directory
img_name = "demo.png"  # Replace with the actual image file name
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

    if output:
        text_detected = True
        for out in output:
            text_bbox, text, text_score = out
            print("Text:", text)
            # Assuming enter_details function takes the license plate text as input
            enter_details(text)  # Call enter_details with the detected text
            time.sleep(5)
# If no text is detected in any of the detected objects
if not text_detected:
    text = 0
    print(text)
    time.sleep(5)


# Function to empty the directory in ownCloud
def empty_directory(directory_path):
    directory_contents = oc.list(directory_path)
    for item in directory_contents:
        oc.delete(item.path)

# Empty the directory
empty_directory(directory_path)
print("Directory emptied successfully.")
