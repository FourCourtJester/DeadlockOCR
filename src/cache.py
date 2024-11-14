from utils import crop_image, crop_image_grayscale, grayscale

import cv2
import json
import numpy
import pickle

CACHE = "./cache"

TEAM_NAMES = ["Amber".upper(), "Sapphire".upper()]

INTENDED_ICON_WIDTH = 83 # Original: 180
INTENDED_ICON_HEIGHT = 103 # Original: 223

CROP_WIDTH = 65
CROP_HEIGHT = 71

ICON_CROP = {
  TEAM_NAMES[0]: (17, 18, 17 + CROP_WIDTH, 18 + CROP_HEIGHT),
  TEAM_NAMES[1]: (1, 18, 1 + CROP_WIDTH, 18 + CROP_HEIGHT)
}

# Load hero icon mappings
with open("./api/heroes.json") as f:
  ALL_HEROES_ICONS = json.load(f)

cache = {
  TEAM_NAMES[0]: {},
  TEAM_NAMES[1]: {},
}

def team_specific_crop(image, team):
  # Resize, Crop and Grayscale
  icon = cv2.resize(image, (INTENDED_ICON_WIDTH, INTENDED_ICON_HEIGHT))
  icon = crop_image(icon, ICON_CROP[team])

  icon_grayscale = grayscale(icon)

  # Generate a content mask
  _, mask = cv2.threshold(icon_grayscale, 1, 255, cv2.THRESH_BINARY)

  return (cv2.cvtColor(icon, cv2.COLOR_RGB2BGR), mask)

# Loop over each hero and preprocess the associated icon
for hero, icon_name in ALL_HEROES_ICONS.items():
  icon_path = f"./api/deadlockapi/heroes/{icon_name}.webp"

  # Load the icon image
  image = cv2.imread(icon_path, cv2.IMREAD_UNCHANGED)

  # Preprocess image as needed
  if image is not None:
    # Apply mask if transparency is present
    if image.shape[2] == 4:
      alpha_channel = image[:, :, 3]
      alpha_mask = alpha_channel > 0

      image = cv2.bitwise_and(image, image, mask=alpha_mask.astype(numpy.uint8))

    # Some images are taller than others
    if image.shape[2] > 223:
      image = crop_image(image, (0, 0, image.shape[2], 223))

    for team in TEAM_NAMES:
      icon, mask = team_specific_crop(image, team)

      # Add the processed image and mask to cache
      cache[team][hero] = { "image": icon, "mask": mask }

      # DEBUG
      cv2.imwrite(f"../test/outputs/camera/{hero}-{team}.jpg", icon)
  else:
      print(f"Failed to load {icon_path}.")

# Save the cache to disk
with open(f"{CACHE}/cache.pkl", "wb") as f:
  pickle.dump(cache, f)

print("Cache generated successfully!")

# Problem Heroes
# - Warden !!
# - Mirage !!
# - Infernus !
# - Seven !
# - Kelvin
# - Dynamo
# - Bebop
# - Haze (Amber)