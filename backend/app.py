from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/strokes', methods=['POST'])
def receive_strokes():
    data = request.get_json()
    if not data or 'strokes' not in data:
        return jsonify({'error': 'No stroke data provided'}), 400

    strokes = data['strokes']
    print("Received Strokes:", strokes)

    return jsonify({'status': 'success', 'message': 'Strokes received'}), 200

if __name__ == '__main__':
    app.run(debug=True)
