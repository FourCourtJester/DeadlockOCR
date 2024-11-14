from datetime import datetime
from flask import jsonify
from utils import crop_image_grayscale_and_resize as crop_image, extract_text_from_image, get_file

import cv2

DEBUG = False
IMAGE_NAME = "image"
TEAM_NAMES = ["Amber", "Sapphire"]

AMBER_SOUL_COORDS = (870, 5, 870 + (920 - 870), 25)  # Based from 1920x1080
SAPPHIRE_SOUL_COORDS = (999, 5, 999 + (1049 - 999), 25)  # (x, y, x2, y2)

# Might be able to use this after we train the font
# TESSERACT_CONFIG = "--psm 7 outputbase digits" # psm 7 assumes a single line of text
TESSERACT_CONFIG = "--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789k" # psm 7 assumes a single line of text

def debug_save(image, team):
  if DEBUG:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S%f")
    filename = f"./test/outputs/souls/{timestamp}-{team}.jpg"

    cv2.imwrite(filename, image)

def debug_print(text):
  if DEBUG:
    print(text)

def fix_soul_icon(text):
  if len(text) > 3:
    return text[1:]
  return text

def endpoint(request, image=None):
  if image == None:
    # Check if an image file was sent in the request
    if IMAGE_NAME not in request.files:
      return jsonify({"error": "No image provided"}), 400

    image = get_file(IMAGE_NAME, request)
    image.load()

  # Ensure an actual file was uploaded
  if image == None:
    return jsonify({"error": "No selected file"}), 400

  # Crop to the areas with the soul totals and compute
  amber_soul_image = crop_image(image, AMBER_SOUL_COORDS)
  amber_souls = extract_text_from_image(amber_soul_image, TESSERACT_CONFIG)[:-1]

  sapphire_soul_image = crop_image(image, SAPPHIRE_SOUL_COORDS)
  sapphire_souls = extract_text_from_image(sapphire_soul_image, TESSERACT_CONFIG)[:-1]

  debug_save(amber_soul_image, "amber")
  debug_save(sapphire_soul_image, "sapphire")

  # Sometimes the souls icon becomes a 6
  amber_souls = fix_soul_icon(amber_souls)
  sapphire_souls = fix_soul_icon(sapphire_souls)

  amber_souls_num = int(amber_souls) if amber_souls.isdigit() else None
  sapphire_souls_num = int(sapphire_souls) if sapphire_souls.isdigit() else None

  debug_print(f"Amber: {amber_souls} | Sapph: {sapphire_souls}")

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