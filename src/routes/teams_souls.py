from datetime import datetime
from flask import jsonify
from utils import crop_image_grayscale as crop_image, extract_text_from_image, get_file

IMAGE_NAME = 'image'
TEAM_NAMES = ['Amber', 'Sapphire']
PROBLEM_TEXT = ['i', 'l', 't', 'I']

AMBER_SOUL_COORDS = (889, 0, 889 + 31, 30)  # Based from 1920x1080
SAPPHIRE_SOUL_COORDS = (1019, 0, 1019 + 31, 30)  # (x, y, x2, y2)

# Might be able to use this after we train the font
# TESSERACT_CONFIG = '--psm 7 outputbase digits' # psm 7 assumes a single line of text

TESSERACT_CONFIG = '--psm 7' # psm 7 assumes a single line of text

def endpoint(request, image=None):
  if image == None:
    # Check if an image file was sent in the request
    if IMAGE_NAME not in request.files:
      return jsonify({"error": "No image provided"}), 400

    image = get_file(IMAGE_NAME, request)
    image.load()

  # Ensure an actual file was uploaded
  if image == None:
    return jsonify({'error': 'No selected file'}), 400

  # Crop to the areas with the soul totals and compute
  amber_soul_image = crop_image(image, AMBER_SOUL_COORDS)
  amber_souls = extract_text_from_image(amber_soul_image, TESSERACT_CONFIG)[:-1]

  sapphire_soul_image = crop_image(image, SAPPHIRE_SOUL_COORDS)
  sapphire_souls = extract_text_from_image(sapphire_soul_image, TESSERACT_CONFIG)[:-1]

  # -- Text replacement because of font
  for char in PROBLEM_TEXT:
    amber_souls = amber_souls.replace(char, '1')
    sapphire_souls = sapphire_souls.replace(char, '1')
  # -- Remove if we revert to outputbase digits

  amber_souls_num = int(amber_souls) if amber_souls.isdigit() else None
  sapphire_souls_num = int(sapphire_souls) if sapphire_souls.isdigit() else None

  # Recycle
  image.close()

  # Return the extracted soul totals as JSON
  return {
    "souls": {
      TEAM_NAMES[0].lower(): amber_souls_num,
      TEAM_NAMES[1].lower(): sapphire_souls_num,
      "delta": (0 if amber_souls_num == None else amber_souls_num) - (0 if sapphire_souls_num == None else sapphire_souls_num)
    }
  }