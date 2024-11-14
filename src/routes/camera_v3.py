from flask import jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import crop_image, get_file, grayscale

import cv2
import json

DEBUG = False

IMAGE_NAME = "image"

TEAM_NAMES = ["Amber".upper(), "Sapphire".upper()]
TEAM_GROUPS = [[0,1,5], [2,4,3]]
TEAM_SIZE = 6

HERO_BOX = {
  "HEIGHT": 79,
  "WIDTH": 87
}
HERO_CROP = {
  TEAM_NAMES[0]: (19, 8, -3),
  TEAM_NAMES[1]: (4, 8, -18),
}
HERO_SPACING = 3

PLAYERS = {
  TEAM_NAMES[0]: {
    "START": (311, 0),
    "DELTAX": HERO_BOX["WIDTH"] + HERO_SPACING,
    "DELTAY": 0,
  },
  TEAM_NAMES[1]: {
    "START": (1051, 0),
    "DELTAX": HERO_BOX["WIDTH"] + HERO_SPACING,
    "DELTAY": 0,
  }
}

THRESHOLD = .65

with open("./src/api/heroes.json", "r") as json_file:
  ALL_HEROES_ICONS = json.load(json_file)

def check_hero(image, team, slot, cache, heroes):
  for hero_name in heroes:
    try:
      data = cache[hero_name]

      hero_image = get_crop(image, team, slot)

      result = cv2.matchTemplate(hero_image, data["image"], cv2.TM_CCOEFF_NORMED, mask=data["mask"])

      _, max_val, _, _ = cv2.minMaxLoc(result)

      # if (max_val >= .3):
        # print(f"{hero_name} on Team {team} in slot {slot} : {max_val}\n")

      if max_val >= THRESHOLD:
        # print(f"{hero_name} on Team {team} in slot {slot} : {max_val}\n")
        return slot

    except Exception as e:
      # print(str(e))
      return None

  return None


def get_crop(image, team, slot):
  xs, y0 = PLAYERS[team]["START"]
  cropxs, cropys, cropxf = HERO_CROP[team]

  x0 = xs + (slot * PLAYERS[team]["DELTAX"])

  coords = (x0 + cropxs, y0 + cropys, x0 + HERO_BOX["WIDTH"] + cropxf, HERO_BOX["HEIGHT"])

  return crop_image(image, coords)

def endpoint(request, image=None):
  if image == None:
    # Check if an image file was sent in the request
    if IMAGE_NAME not in request.files:
      return jsonify({"error": "No image provided"}), 400

    image = get_file(IMAGE_NAME, request)

  # Ensure an actual file was uploaded
  if image == None:
    return jsonify({"error": "No selected file"}), 400

  cache = request.deadlockcache

  all_heroes = cache.get(TEAM_NAMES[0]).keys()
  heroes = request.form.getlist("heroes") if len(request.form.getlist("heroes")) else all_heroes

  image = grayscale(image)

  result = {
    "camera": {
      "slot": -1,
      "team": None,
      "player": None,
    }
  }

  with ThreadPoolExecutor(max_workers=3) as executor:
    for team_index, team in enumerate(TEAM_NAMES):
      for group in TEAM_GROUPS:
        futures = [
          executor.submit(check_hero, image, team, slot, cache.get(team), heroes)
          for slot in group
        ]

        for future in as_completed(futures):
          camera = future.result()

          # If a player is found, map player to the appropriate slot and return
          if camera is not None:
            player_slot = (team_index * TEAM_SIZE) + camera

            return {
              "camera": {
                "slot": player_slot,
                "team": team,
                "player": camera
              }
            }

  return result