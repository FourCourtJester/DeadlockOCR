from flask import jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import crop_image_grayscale as crop_image, extract_text_from_image, get_file

# import cv2

IMAGE_NAME = 'image'
TEAM_NAMES = ['Amber', 'Sapphire']
TEAM_SIZE = 6

GROUP_AMT = 2
PLAYERS_PER_GROUP = 3

BOUNDING_BOX = {
  "HEIGHT": 24,
  "WIDTH": 85
}

PLAYERS = {
  TEAM_NAMES[0].upper(): {
    "START": (312, 120),
    "DELTAX": BOUNDING_BOX["WIDTH"] + 5,
    "DELTAY": 0,
  },
  TEAM_NAMES[1].upper(): {
    "START": (1052, 120),
    "DELTAX": BOUNDING_BOX["WIDTH"] + 5,
    "DELTAY": 0,
  }
}

TESSERACT_CONFIG = '--oem 3 --psm 6 -l eng+fra' # psm 6 can handle multiple lines

def get_coords(team, i):
  """Gets the current iterations coordinates"""
  # Get the original x/y
  x0, y = PLAYERS[team]["START"]

  # Iterate to get the new bounding box
  x = x0 + (i * PLAYERS[team]["DELTAX"])

  return (x, y, x + BOUNDING_BOX["WIDTH"], y + BOUNDING_BOX["HEIGHT"])

def get_player_name(image, team, player):
  """Get the player name"""
  # Crop to the areas with the player names
  name_image = crop_image(image, get_coords(team.upper(), player))

  # Get the player name
  return {
    "name": extract_text_from_image(name_image, TESSERACT_CONFIG),
    "player": player
  }

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

  result = {
    "players": {
      TEAM_NAMES[0].lower(): [None] * 6,
      TEAM_NAMES[1].lower(): [None] * 6,
    }
  }

  with ThreadPoolExecutor(max_workers=3) as executor:
    for team_index, team in enumerate(TEAM_NAMES):
      for group_index in range(GROUP_AMT):
        # Submit all player checks in the group at once
        futures = [
          executor.submit(get_player_name, image, team, (group_index * PLAYERS_PER_GROUP) + player_index)
          for player_index in range(PLAYERS_PER_GROUP)
        ]

        for future in as_completed(futures):
          name, player = future.result()["name"], future.result()["player"]

          # Save the text
          result['players'][team.lower()][player] = name.replace('\n', ' ') if name else None

  # Recycle
  image.close()

  # Return the extracted soul totals as JSON
  return result