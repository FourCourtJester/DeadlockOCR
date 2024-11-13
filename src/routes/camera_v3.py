from flask import jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import crop_image_grayscale as crop_image, get_file

import cv2
import numpy

DEBUG = False

IMAGE_NAME = 'image'
TEAM_NAMES = ['Amber', 'Sapphire']

def debug_save(image, name):
  if DEBUG:
    filename = f"./test/outputs/camera/{name}"

    cv2.imwrite(filename, image)

def get_coords():
  """Gets the current iterations coordinates"""
  return (330, 0, 394, 78)

def resize_image(image):
  return cv2.resize(image, (79, 98))

def endpoint(request, image=None):
  if image == None:
    # Check if an image file was sent in the request
    if IMAGE_NAME not in request.files:
      return jsonify({"error": "No image provided"}), 400

    image = get_file(IMAGE_NAME, request)
    image.convert("RGB")

  # Ensure an actual file was uploaded
  if image == None:
    return jsonify({'error': 'No selected file'}), 400

  hero = cv2.imread("./src/icons/heroes/wraith.webp", cv2.IMREAD_UNCHANGED)

  # Strip transparencies
  if hero.shape[2] == 4:
    bgr_image = hero[:, :, :3]
    alpha_channel = hero[:, :, 3]

    mask_alpha = alpha_channel > 0
    hero = cv2.bitwise_and(bgr_image, bgr_image, mask=mask_alpha.astype(numpy.uint8))

  hero = resize_image(hero)
  template = crop_image(hero, (15, 0, 79, 78))

  _, mask = cv2.threshold(template, 1, 255, cv2.THRESH_BINARY)

  hero_location = crop_image(image, get_coords())

  debug_save(numpy.array(image), 'screenshot.jpg')
  debug_save(template, 'template.png')
  debug_save(hero_location, 'topbar.jpg')

  is_hero = cv2.matchTemplate(hero_location, template, cv2.TM_CCOEFF_NORMED, mask=mask)

  _, max_val, _, _ = cv2.minMaxLoc(is_hero)
  print(f"Best match confidence: {max_val}")

# TODO: Pass array of hero names to reduce complexity (ie, only calculate 12 heroes instead of 30)
# TODO: Amber AND Sapphire hero bounds
# TODO: Preprocess and cache all the .webp and their masks on startup
# TODO: Loop over all 12 hero spots
# TODO: Death detection?
# TODO: Does grayscale remove color considerations for highlights in early game?
# TODO: Map all the random hero names to their icons