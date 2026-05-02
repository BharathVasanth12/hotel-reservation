from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# Load the trained model
MODEL_PATH = 'artifacts/model/hotel_reservation_model.joblib'
model = None

def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"✅ Model loaded successfully from {MODEL_PATH}")
    else:
        print(f"⚠️  Model not found at {MODEL_PATH}. Please train the model first.")

@app.route('/')
def home():
    """Render the main prediction page"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests"""
    try:
        if model is None:
            return jsonify({
                'error': 'Model not loaded. Please train the model first.'
            }), 500
        
        # Get data from request
        data = request.get_json()
        
        # Convert to dataframe
        input_df = pd.DataFrame([data])
        
        # Make prediction
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0]
        
        # Get probability of cancellation (class 1)
        cancel_probability = float(probability[1])
        
        return jsonify({
            'prediction': int(prediction),
            'probability': cancel_probability,
            'status': 'Cancelled' if prediction == 1 else 'Confirmed'
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Prediction failed: {str(e)}'
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None
    })

if __name__ == '__main__':
    load_model()
    app.run(debug=True, host='0.0.0.0', port=5001)
