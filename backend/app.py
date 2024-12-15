from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import torch.nn as nn
import json
from torch.nn.utils.rnn import pad_sequence
from training.stroke_classifier import StrokeLSTMClassifier
from latex_generator import LatexGenerator

app = Flask(__name__)
CORS(app)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load label mapping from JSON file
with open('training_data/label_mapping.json', 'r') as f:
    label_mapping = json.load(f)

num_classes = len(label_mapping)
model = StrokeLSTMClassifier(
    input_size=3,
    hidden_size=128,
    num_layers=2,
    num_classes=num_classes,
    dropout=0.3,
    bidirectional=True
).to(device)

latex = LatexGenerator()

# Load trained model
model.load_state_dict(torch.load('training/lstm_model.pth', map_location=device, weights_only=True))
model.eval()


def preprocess_input(stroke_sequences):
    # Convert 2D list of dictionaries to list of stroke tensors
    strokes = [
        torch.tensor([[point['x'], point['y'], point['t']] for point in stroke], dtype=torch.float32)
        for stroke in stroke_sequences
    ]

    normalized_strokes = []
    for stroke in strokes:
        # Clone the tensor to avoid in-place modification issues
        stroke = stroke.clone()

        # Normalize relative positions
        normalized_stroke = stroke - stroke[0]

        # Avoid division by zero
        max_x = torch.max(torch.abs(stroke[:, 0]))
        max_y = torch.max(torch.abs(stroke[:, 1]))
        max_x = max_x if max_x > 0 else 1.0
        max_y = max_y if max_y > 0 else 1.0

        # Normalize points
        normalized_stroke[:, 0] = normalized_stroke[:, 0] / max_x
        normalized_stroke[:, 1] = normalized_stroke[:, 1] / max_y

        # Update strokes list with normalized stroke
        normalized_strokes.append(normalized_stroke)

    # Pad sequences to same length
    padded_strokes = pad_sequence(strokes, batch_first=True, padding_value=0.0)

    return padded_strokes.to(device)


def predict(stroke_sequences):
    """
    Predicts the class labels for given stroke sequences.

    Args:
        stroke_sequences (list of list of lists): Each stroke sequence is a list of [x, y, t] points.

    Returns:
        list: Predicted class labels.
    """
    inputs = preprocess_input(stroke_sequences)

    with torch.no_grad():
        outputs = model(inputs)
        _, predicted = torch.max(outputs, 1)
        predicted_labels = [label_mapping[str(label.item())] for label in predicted]

    return predicted_labels


@app.route('/api/strokes', methods=['POST'])
def receive_strokes():
    data = request.get_json()
    if not data or 'strokes' not in data:
        return jsonify({'error': 'No stroke data provided'}), 400

    stroke_sequences = data['strokes']

    if not isinstance(stroke_sequences, list) or not all(isinstance(seq, list) for seq in stroke_sequences):
        return jsonify({'error': 'Invalid stroke data format.'}), 400

    try:
        predictions = predict(stroke_sequences)
        latex.add_symbols(predictions)
        return jsonify({'predictions': stroke_sequences}), 500
    except Exception as e:
        pass
        return jsonify({'error': e}), 200


if __name__ == '__main__':
    app.run(debug=True)
