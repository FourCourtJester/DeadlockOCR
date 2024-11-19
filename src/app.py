from flask import Flask, copy_current_request_context, g, jsonify, request
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor

from routes.teams_souls import endpoint as teams_souls
from routes.player_names import endpoint as player_names
from routes.camera_v3 import endpoint as camera
from routes.spectator import endpoint as spectator

import os
import pickle

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=5)

CORS(app, origins=["http://localhost:3000"])

CACHE_PATH = "./cache/cache.pkl" if os.getenv("FLASK_ENV") == "production" else "./src/cache/cache.pkl"

def endpoint_with_context(func, *args, **kwargs):
  @copy_current_request_context
  def fn():
    return func(*args, **kwargs)

  future = executor.submit(fn)
  return future.result()

@app.before_request
def cache():
  if "cache" not in g:
    with open(CACHE_PATH, "rb") as f:
      g.cache = pickle.load(f)

@app.route("/deadlock/ocr/teams/souls", methods=["POST"])
def route_teams_souls():
  try:
    return jsonify(endpoint_with_context(teams_souls, request))

  except Exception as e:
    return jsonify({"error": str(e)}), 500  # Return the error message

@app.route("/deadlock/ocr/teams/players", methods=["POST"])
def route_player_names():
  try:
    return jsonify(endpoint_with_context(player_names, request))

  except Exception as e:
    return jsonify({"error": str(e)}), 500  # Return the error message

@app.route("/deadlock/ocr/camera", methods=["POST"])
def route_camera():
  try:
    request.deadlockcache = g.cache
    return jsonify(endpoint_with_context(camera, request))

  except Exception as e:
    return jsonify({"error": str(e)}), 500  # Return the error message

# Aggregate
@app.route("/deadlock/ocr/spectator", methods=["POST"])
def route_spectator():
  try:
    result = endpoint_with_context(spectator, request)

    return jsonify(result)

  except Exception as e:
    return jsonify({"error": str(e)}), 500  # Return the error message

# Development server
if os.getenv('FLASK_ENV') == "development":
  if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
