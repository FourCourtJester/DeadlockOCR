from flask import copy_current_request_context, jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import get_file

from routes.teams_souls import endpoint as teams_souls
from routes.player_names import endpoint as player_names
from routes.camera import endpoint as camera

IMAGE_NAME = 'image'

def endpoint(request):
  def endpoint_with_context(endpoint):
    if endpoint == 'teams_souls':
      return teams_souls(request, image=image.copy())
    elif endpoint == 'player_names':
      return player_names(request, image=image.copy())
    elif endpoint == 'camera':
      return camera(request, image=image.copy())

  # Check if an image file was sent in the request
  if IMAGE_NAME not in request.files:
    return jsonify({"error": "No image provided"}), 400

  image = get_file(IMAGE_NAME, request)
  image.load()

  # Ensure an actual file was uploaded
  if image == None:
    return jsonify({'error': 'No selected file'}), 400

  endpoints = request.form.getlist('endpoints')
  result = {}

  with ThreadPoolExecutor(max_workers=5) as executor:
    futures = []

    for endpoint in endpoints:
      futures.append(executor.submit(endpoint_with_context, endpoint))

    for future in as_completed(futures):
      try:
        task = future.result(timeout=0.5)
        result.update(task)
      except Exception as e:
        print(f"Error occurred while processing the future: {e}")

  # Recycle
  image.close()

  return result