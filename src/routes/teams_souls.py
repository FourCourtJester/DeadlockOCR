from flask import jsonify
from utils import crop_image, extract_text_from_image, get_file

TEAM_1_SOUL_COORDS = (885, 0, 885 + 35, 30)  # Based from 1920x1080
TEAM_2_SOUL_COORDS = (1015, 0, 1015 + 35, 30)  # (x, y, x2, y2)
TESSERACT_CONFIG = '--psm 7 outputbase digits' # psm 7 assumes a single line of text

def endpoint(request):
  # Check if an image file was sent in the request
  if 'image' not in request.files:
      return jsonify({"error": "No image provided"}), 400

  image = get_file('image', request)

  # Ensure an actual file was uploaded
  if image == None:
    return jsonify({'error': 'No selected file'}), 400

  # Crop to the areas with the soul totals and compute
  amber_soul_image = crop_image(image, TEAM_1_SOUL_COORDS)
  amber_souls = extract_text_from_image(amber_soul_image, TESSERACT_CONFIG)

  sapphire_soul_image = crop_image(image, TEAM_2_SOUL_COORDS)
  sapphire_souls = extract_text_from_image(sapphire_soul_image, TESSERACT_CONFIG)

  # Return the extracted soul totals as JSON
  return jsonify({
      "souls": {
          "amber": int(amber_souls) if amber_souls.isdigit() else None,
          "sapphire": int(sapphire_souls) if sapphire_souls.isdigit() else None,
      }
  })