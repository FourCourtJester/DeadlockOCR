from flask import jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import crop_image, get_file

import numpy
# import cv2

IMAGE_NAME = 'image'
TEAM_NAMES = ['Amber', 'Sapphire']
TEAM_SIZE = 6

GROUP_AMT = 2
PLAYERS_PER_GROUP = 3

HIGHLIGHT_SUCCESS = 34
HIGHLIGHT = {
   "WHITE": [numpy.array([188,175,159]), numpy.array([240,225,202])]
}

BOUNDING_BOX = {
   "HEIGHT": 48,
   "WIDTH": 85
}

PLAYERS = {
   TEAM_NAMES[0].upper(): {
      "START": (312, 0),
      "DELTAX": BOUNDING_BOX["WIDTH"] + 5,
      "DELTAY": 0,
   },
   TEAM_NAMES[1].upper(): {
      "START": (1052, 0),
      "DELTAX": BOUNDING_BOX["WIDTH"] + 5,
      "DELTAY": 0,
   }
}

def get_coords(team, i):
  """Gets the current iterations coordinates"""
  # Get the original x/y
  x0, y = PLAYERS[team]["START"]

  # Iterate to get the new bounding box
  x = x0 + (i * PLAYERS[team]["DELTAX"])

  return (x, y, x + BOUNDING_BOX["WIDTH"], y + BOUNDING_BOX["HEIGHT"])

def detect_color_percentage(image, bounds):
    """Returns the results of the percentage of the image being a certain color"""
    # Convert to Numpy for efficient pixel analysis
    total_pixels = image.shape[0] * image.shape[1]

    # Create boolean mask for pixels within the color range
    mask = numpy.all((image >= bounds[0]) & (image <= bounds[1]), axis=-1)

    # Count the number of pixels that fall within the color range
    color_pixels = numpy.sum(mask)

    # Calculate the percentage of pixels within the range
    percentage = (color_pixels / total_pixels) * 100
    return percentage

def get_camera(image, team, player):
  """Check if this player is the current camera"""
  # Crop to the areas with the player names
  hero_image = crop_image(image, get_coords(team.upper(), player))

  # Get the player name
  if detect_color_percentage(hero_image, HIGHLIGHT["WHITE"]) >= HIGHLIGHT_SUCCESS:
      return player
  return None

def endpoint(request):
  # Check if an image file was sent in the request
  if IMAGE_NAME not in request.files:
      return jsonify({"error": "No image provided"}), 400

  image = get_file(IMAGE_NAME, request)
  image = image.convert("RGB")

  # Ensure an actual file was uploaded
  if image == None:
    return jsonify({'error': 'No selected file'}), 400

  result = {
    "camera": -1,
    "team": None,
    "player": None,
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

            return jsonify({
              "camera": player_slot,
              "team": team,
              "player": camera
            })

  return jsonify(result)