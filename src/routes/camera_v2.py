from flask import jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import crop_image, get_file

import numpy
import cv2

IMAGE_NAME = 'image'
TEAM_NAMES = ['Amber', 'Sapphire']
TEAM_SIZE = 6

GROUP_AMT = 2
PLAYERS_PER_GROUP = 3

BOUNDING_BOX = {
  "HEIGHT": 56,
  "WIDTH": 79
}

EDGE = 4

PLAYERS = {
  TEAM_NAMES[0].upper(): {
    "START": (315, 0),
    "DELTAX": BOUNDING_BOX["WIDTH"] + 11,
    "DELTAY": 0,
  },
  TEAM_NAMES[1].upper(): {
    "START": (1055, 0),
    "DELTAX": BOUNDING_BOX["WIDTH"] + 11,
    "DELTAY": 0,
  }
}

def get_coords(team, i):
  """Gets the current iterations coordinates"""
  # Get the original x/y
  x0, y = PLAYERS[team]["START"]

  # Iterate to get the new bounding box
  x = x0 + (i * PLAYERS[team]["DELTAX"])

  return (x - EDGE, y, x + BOUNDING_BOX["WIDTH"] + EDGE, y + BOUNDING_BOX["HEIGHT"])

def detect_color_percentage(image):
    """Returns the results of the percentage of the image being a certain color"""
    left_edge = image[:, :EDGE]
    right_edge = image[:, -EDGE:]

    low_white = numpy.array([100, 100, 100])
    high_white = numpy.array([255, 255, 255])

    mask_left = cv2.inRange(left_edge, low_white, high_white)
    mask_right = cv2.inRange(right_edge, low_white, high_white)

    left_ratio = numpy.sum(mask_left == 255) / mask_left.size
    right_ratio = numpy.sum(mask_right == 255) / mask_right.size

    return left_ratio + right_ratio >= 2

def get_camera(image, team, player):
  """Check if this player is the current camera"""
  # Crop to the areas with the player names
  hero_image = crop_image(image, get_coords(team.upper(), player))
  select_check = detect_color_percentage(hero_image)

  # print(f"{team} {player}: {select_check}")

  # Get the player name
  if select_check:
    return player

  return None

def endpoint(request, image=None):
  if image == None:
    # Check if an image file was sent in the request
    if IMAGE_NAME not in request.files:
      return jsonify({"error": "No image provided"}), 400

    image = get_file(IMAGE_NAME, request)
    image = image.convert("RGB")

  # Ensure an actual file was uploaded
  if image == None:
    return jsonify({'error': 'No selected file'}), 400

  result = {
    "camera": {
      "slot": -1,
      "team": None,
      "player": None,
    }
  }

  with ThreadPoolExecutor(max_workers=3) as executor:
    for team_index, team in enumerate(TEAM_NAMES):
      for group_index in range(GROUP_AMT):
        # Submit all player checks in the group at once
        futures = [
          executor.submit(get_camera, image, team, (group_index * PLAYERS_PER_GROUP) + player_index)
          for player_index in range(PLAYERS_PER_GROUP)
        ]

        for future in as_completed(futures):
          camera = future.result()

          # If a player is found, map player to the appropriate slot and return
          if camera is not None:
            player_slot = (team_index * TEAM_SIZE) + camera

            # Recycle
            image.close()

            return {
              "camera": {
                "slot": player_slot,
                "team": team,
                "player": camera
              }
            }

  # Recycle
  image.close()

  return result