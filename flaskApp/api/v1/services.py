import numpy as np
import cv2
import re
import easyocr
from PIL import Image
from keras.preprocessing import image as keras_image
from keras.models import load_model
import os

def load_image_model():
    model = load_model('models/image_model.h5')
    return model

def predict_sensitivity(model, file):
    img = keras_image.load_img(file, target_size=(150, 150))
    x = keras_image.img_to_array(img)
    x = np.expand_dims(x, axis=0)

    images = np.vstack([x])
    classes = model.predict(images, batch_size=10)
    if classes[0]>0.5:
        return "sensitive"
    else:
        return "non-sensitive"
    
def detect_texts(image): 
    reader = easyocr.Reader(['en'])
    output = reader.readtext(image, paragraph=True)
    return output

def find_matching_texts(regex, texts):
    matching_texts = []
    for text in texts:
        matches = re.findall(regex, text[1])
        if len(matches) != 0:
            matching_texts.append(text)       
    return matching_texts

def blur_matching_text(matching_texts, image):
    for matching_text in matching_texts:
        cord = matching_text[0]
        # Get bounding box coordinates
        x_min, y_min = [int(min(idx)) for idx in zip(*cord)]
        x_max, y_max = [int(max(idx)) for idx in zip(*cord)]

        # Define region of interest (ROI)
        topLeft = (x_min, y_min)
        bottomRight = (x_max, y_max)
        x, y = topLeft[0], topLeft[1]
        w, h = bottomRight[0] - topLeft[0], bottomRight[1] - topLeft[1]

        # Apply Gaussian blur to the ROI
        ROI = image[y:y+h, x:x+w]
        blur = cv2.GaussianBlur(ROI, (51, 51), 0)

        # Replace ROI with blurred version in the image
        image[y:y+h, x:x+w] = blur
    return image

def detect_sensitive_info(file):
    try:
        os.remove("outputs/blurred_image.jpg")
    except: 
        pass
    image = Image.open(file)
    image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
    model = load_image_model()
    sensitivity = predict_sensitivity(model, file)
    if sensitivity == 'non-sensitive':
        return "Image is non-sensitive"
    else:
        texts = detect_texts(image)
        # print("texts :", texts)
        regex = "((?<!\d)(\d{4}\s\d{4}\s\d{4})(?!\d))|([A-Za-z]{5}[0-9]{4}[A-Za-z]{1})|((?<!\d)(\d{4}\s\d{4}\s\d{4}\s\d{4})(?!\d))|(\d{2}/\d{2})|(\d{2}/\d{2}/\d{4})"
        matching_texts = find_matching_texts(regex, texts)
        # print("matching texts :", matching_texts)
        if len(matching_texts) > 0:
            blurred_image = blur_matching_text(matching_texts, image)
            cv2.imwrite("outputs/blurred_image.jpg", blurred_image)
            return blurred_image
        else :
            return "Could not find any mathing patterns."