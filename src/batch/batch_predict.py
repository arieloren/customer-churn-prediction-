import sys
import os
import pandas as pd

from src.common.extract import ExtractFile
from src.common.preprocessing import DataPreprocessor
from src.common.model_loader import TransformModel
import config


def main(input_file):
    # 1. Load data
    extractor = ExtractFile(input_file)
    raw_data = extractor.load_data()

    # 2. Preprocess
    preprocessor = DataPreprocessor()
    preprocessor.fit(raw_data)  # only needed if you're recalculating mean, optional in prod
    processed_data = preprocessor.transform(raw_data)
    print(processed_data.columns.tolist())
    print(config.MODEL_COLUMNS)

    # 3. Load model and predict
    model = TransformModel(config)
    predictions = model.predict(processed_data)

    # 4. Output result
    output = raw_data.copy()
    output['Prediction'] = predictions
    print(output[['Prediction']].head())  # preview
    output.to_csv("outputs/predictions.csv", index=False)
    print("✅ Predictions saved to outputs/predictions.csv")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Please provide the path to the input CSV file.")
        print("Usage: python batch_predict.py data/database_input.csv")
        sys.exit(1)

    input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print(f"❌ File not found: {input_path}")
        sys.exit(1)

    main(input_path)
