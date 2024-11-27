from datetime import datetime
from flask import jsonify
from utils import crop_image_grayscale_and_resize as crop_image, extract_text_from_image, get_file

import cv2
import re

DEBUG = False
IMAGE_NAME = "image"
TEAM_NAMES = ["Amber", "Sapphire"]

AMBER_SOUL_COORDS = (882, 5, 882 + (920 - 882), 25)  # Based from 1920x1080
SAPPHIRE_SOUL_COORDS = (1011, 5, 1011 + (1049 - 1011), 25)  # (x, y, x2, y2)

TESSERACT_MODEL = "retaildemo-bold"
TESSERACT_CONFIG = f"--oem 3 --psm 7 -l {TESSERACT_MODEL}" # psm 7 assumes a single line of text

def debug_save(image, team):
  if DEBUG:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S%f")
    filename = f"./test/outputs/souls/{timestamp}-{team}.jpg"

    cv2.imwrite(filename, image)

def debug_print(text):
  if DEBUG:
    print(text)

def fix(team):
  result = re.search(r"\d+k", team)

  # Regex failed, likely due to Tesseract precision
  if result is None:
    return None

  # Regex success, hopefully correct
  return result.group().strip()

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
  amber_souls = extract_text_from_image(amber_soul_image, TESSERACT_CONFIG)

  sapphire_soul_image = crop_image(image, SAPPHIRE_SOUL_COORDS)
  sapphire_souls = extract_text_from_image(sapphire_soul_image, TESSERACT_CONFIG)

  # debug_print(f"Amber: \"{amber_souls}\" | Sapph: \"{sapphire_souls}\"")

  # debug_save(amber_soul_image, "amber")
  # debug_save(sapphire_soul_image, "sapphire")

  amber_souls = fix(amber_souls)
  sapphire_souls = fix(sapphire_souls)

  debug_print(f"Amber: \"{amber_souls}\" | Sapph: \"{sapphire_souls}\"")

  if amber_souls is None or sapphire_souls is None:
    return {
      "souls": {
        TEAM_NAMES[0].lower(): None,
        TEAM_NAMES[1].lower(): None,
        "delta": None
      }
    }

  # Recycle
  image.close()

  # Return the extracted soul totals as JSON
  return {
    "souls": {
      TEAM_NAMES[0].lower(): int(amber_souls[:-1]),
      TEAM_NAMES[1].lower(): int(sapphire_souls[:-1]),
      "delta": int(amber_souls[:-1]) - int(sapphire_souls[:-1])
    }
  }