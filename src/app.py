from flask import Flask, request, jsonify

from routes.teams_souls import endpoint as teams_souls

app = Flask(__name__)

@app.route('/deadlock/ocr/teams/souls', methods=['POST'])
def route_teams_souls():
    try:
      return teams_souls(request)

    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Return the error message

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
