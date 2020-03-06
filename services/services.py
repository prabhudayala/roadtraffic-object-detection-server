import os
from werkzeug.utils import secure_filename
import imutils
import cv2
import base64
import os
import cv2
import numpy as np
import tensorflow as tf
import sys


from utils import label_map_util
from utils import visualization_utils as vis_util

stopper = False


global MODEL_NAME
MODEL_NAME = 'trained-inference-graphs' #'inference_graph'

global CWD_PATH
CWD_PATH = os.getcwd()

global PATH_TO_CKPT
PATH_TO_CKPT = os.path.join(
    CWD_PATH, 'services', 'frozen_inference_graph.pb')

global PATH_TO_LABELS
PATH_TO_LABELS = os.path.join(CWD_PATH, 'services', 'label_map.pbtxt')
global NUM_CLASSES
NUM_CLASSES = 15

global label_map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)

global categories
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)

global category_index
category_index = label_map_util.create_category_index(categories)

global detection_graph
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

global sess
sess = tf.Session(graph=detection_graph)

global image_tensor
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

global detection_boxes
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

global detection_scores
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')

global detection_classes
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

global num_detections
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

def process_image(reqData, upload_folder):
    try:

        f = reqData.files['file']
        file_save_path = os.path.join(
            upload_folder, "images", secure_filename(f.filename))
        f.save(file_save_path)

        image = cv2.imread(os.path.join(file_save_path))

        image_expanded = np.expand_dims(image, axis=0)

        # Perform the actual detection by running the model with the image as input
        (boxes, scores, classes, num) = sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict={image_tensor: image_expanded})

        # Draw the results of the detection (aka 'visulaize the results')

        vis_util.visualize_boxes_and_labels_on_image_array(
            image,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            category_index,
            use_normalized_coordinates=True,
            line_thickness=8,
            min_score_thresh=0.60)

        _, img_encoded = cv2.imencode(".jpg", image)
        imag64 = base64.b64encode(img_encoded)
        # print(imag64)
        return imag64
    except Exception as e:
        print(e)


def process_live():
    
    cap = cv2.VideoCapture(0)
    ret = cap.set(3,1280)
    ret = cap.set(4,720)
    global stopper

    while True:
        ret, frame = cap.read()
        frame_expanded = np.expand_dims(frame, axis=0)

        # Perform the actual detection by running the model with the image as input
        (boxes, scores, classes, num) = sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict={image_tensor: frame_expanded})

        # Draw the results of the detection (aka 'visulaize the results')
        vis_util.visualize_boxes_and_labels_on_image_array(
            frame,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            category_index,
            use_normalized_coordinates=True,
            line_thickness=8,
            min_score_thresh=0.60)
        (flag, encodeImg) = cv2.imencode(".jpg", frame)

        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
              bytearray(encodeImg) + b'\r\n')
        if stopper == True:
            break


def stop_stream():
    global stopper
    stopper = True
