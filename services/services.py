import os
from werkzeug.utils import secure_filename
import imutils
import cv2
import base64


def process_image(reqData, upload_folder):
    try:
        f = reqData.files['file']
        file_save_path = os.path.join(
            upload_folder, "images", secure_filename(f.filename))
        f.save(file_save_path)

        image = cv2.imread(os.path.join(file_save_path))
        _, img_encoded = cv2.imencode(".jpg", image)
        imag64 = base64.b64encode(img_encoded)
        # print(imag64)
        return imag64
    except Exception as e:
        print(e)
