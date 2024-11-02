from PIL import Image

import numpy
import cv2
import pytesseract

def crop_image(image, coords):
    """Crop the image to specific coordinates."""
    x,y,w,h = coords

    np_image = numpy.array(image)

    cropped_image = np_image[y:h, x:w]
    grayscale_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
    resized_image = cv2.resize(grayscale_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)


    return resized_image

def extract_text_from_image(image, config):
    """Use Tesseract to extract text from the image."""
    text = pytesseract.image_to_string(image, config=config)
    return text.strip()

def get_file(name, request):
    """Get the named file from the POST for processing"""
    file = request.files[name]

    if file.filename == '':
      return None

    # Load the image from the POST file upload
    return Image.open(file)