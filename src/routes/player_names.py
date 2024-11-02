from flask import jsonify
from utils import crop_image, extract_text_from_image, get_file

# import cv2

PLAYERS = {
   "AMBER": {
      "START": (312, 120),
      "DELTAX": 90,
      "DELTAY": 0,
   },
   "SAPPHIRE": {
      "START": (1052, 120),
      "DELTAX": 90,
      "DELTAY": 0,
   }
}
BOUNDING_BOX = {
   "HEIGHT": 24,
   "WIDTH": 85
}

TESSERACT_CONFIG = '--oem 3 --psm 6 -l eng+fra' # psm 6 can handle multiple lines

def get_coords(team, i):
  """Gets the current iterations coordinates"""
  # Get the original x/y
  x0, y = PLAYERS[team]["START"]

  # Iterate to get the new bounding box
  x = x0 + (i * PLAYERS[team]["DELTAX"])

  return (x, y, x + BOUNDING_BOX["WIDTH"], y + BOUNDING_BOX["HEIGHT"])


def endpoint(request):
  # Check if an image file was sent in the request
  if 'image' not in request.files:
      return jsonify({"error": "No image provided"}), 400

  image = get_file('image', request)

  # Ensure an actual file was uploaded
  if image == None:
    return jsonify({'error': 'No selected file'}), 400

  result = {
    "players": {
      "amber": [],
      "sapphire": [],
    }
  }

  for team in ['amber', 'sapphire']:
    for i in range(6):
      # Crop to the areas with the player names
      name_image = crop_image(image, get_coords(team.upper(), i))

      # DEBUG: save files for visual inspection
      # cv2.imwrite("".join(["./test/outputs/", team, str(i), request.files['image'].filename]), name_image)

      # Get the player name
      name = extract_text_from_image(name_image, TESSERACT_CONFIG)

      # Save the text
      result['players'][team].append(name if name else None)

  # Return the extracted soul totals as JSON
  return jsonify(result)