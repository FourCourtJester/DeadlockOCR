from flask import jsonify

import pytesseract
import numpy as np
import cv2

TEAM_1_SOUL_COORDS = (870, 0, 870 + 50, 30)  # Based from 1920x1080
TEAM_2_SOUL_COORDS = (999, 0, 999 + 50, 30)  # (x, y, x2, y2)

def crop_image(image, coords):
    """Crop the image to specific coordinates."""
    x, y, w, h = coords
    return image[y:h, x:w]

def extract_text_from_image(cropped_image):
    """Use Tesseract to extract text from the cropped image."""
    text = pytesseract.image_to_string(cropped_image, config='--psm 7 outputbase digits')  # psm 7 assumes a single line of text
    return text.strip()

def endpoint(request):
  # Check if an image file was sent in the request
  if 'image' not in request.files:
      return jsonify({"error": "No image provided"}), 400

  # Read the image as a numpy array from the incoming file
  file = request.files['image']

  # Ensure an actual file was uploaded
  if file.filename == '':
    return jsonify({'error': 'No selected file'}), 400

  image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

  # Crop to the areas with the soul totals and compute
  amber_soul_image = crop_image(image, TEAM_1_SOUL_COORDS)
  amber_souls = extract_text_from_image(amber_soul_image)

  sapphire_soul_image = crop_image(image, TEAM_2_SOUL_COORDS)
  sapphire_souls = extract_text_from_image(sapphire_soul_image)

  # Return the extracted soul totals as JSON
  return jsonify({
      "souls": {
          "amber": int(amber_souls) if amber_souls.isdigit() else None,
          "sapphire": int(sapphire_souls) if sapphire_souls.isdigit() else None,
      }
  })