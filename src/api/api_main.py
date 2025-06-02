from flask import Flask, request, jsonify
from marshmallow import ValidationError
import pandas as pd

from request_schema import CustomerChurnRequestSchema
from src.common.preprocessing import DataPreprocessor
from src.common.model_loader import TransformModel
from config.config_loader import Config

app = Flask(__name__)
# Load configuration
config = Config()

# Instantiate components
schema = CustomerChurnRequestSchema()
preprocessor = DataPreprocessor()
model = TransformModel(config)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        request_data = request.get_json()
        validated_data = schema.load(request_data)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    # Convert to DataFrame for processing
    df = pd.DataFrame([validated_data])

    # Preprocess + Predict
    preprocessor.fit(df) 
    processed = preprocessor.transform(df)
    prob = model.predict_proba(processed)[0][1]  # Get probability of class=1
    prediction = int(prob >= config.get_threshold())   # Use threshold to determine 0/1

    return jsonify({
        "prediction": prediction,
        "probability": round(prob, 3)
    }), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9999, debug=True)
