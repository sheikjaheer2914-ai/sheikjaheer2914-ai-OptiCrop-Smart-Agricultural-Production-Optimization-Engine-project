import os
import pickle
import numpy as np
from flask import Flask, render_template, request

app = Flask(__name__)
MODEL_PATH = os.path.join('models', 'best_crop_model.pkl')

def load_prediction_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file missing at: {MODEL_PATH}")
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)

try:
    engine_payload = load_prediction_model()
    if isinstance(engine_payload, dict):
        model = engine_payload.get('model')
    else:
        model = engine_payload
    print("✅ Success: Machine Learning Model Loaded Safely!")
except Exception as e:
    print(f"⚠️ Model Initialization Warning: {e}")
    model = None

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return render_template('index.html', error="The backend server model is uninitialized.")
    try:
        scenario = request.form.get('scenario', '1')
        N = float(request.form.get('N', 0))
        P = float(request.form.get('P', 0))
        K = float(request.form.get('K', 0))
        temp = float(request.form.get('temperature', 0))
        humid = float(request.form.get('humidity', 0))
        ph = float(request.form.get('ph', 0))
        rain = float(request.form.get('rainfall', 0))
        
        if ph < 0 or ph > 14:
            raise ValueError("The Soil pH Value must be between 0.0 and 14.0.")
            
        feature_vector = np.array([[N, P, K, temp, humid, ph, rain]])
        prediction_output = model.predict(feature_vector)
        predicted_crop = str(prediction_output).capitalize()
        
        # --- AUTOMATIC SYSTEM-WIDE SOIL HEALTH SCREENING ---
        auto_alerts = []
        if N < 40: auto_alerts.append("Critical Low Nitrogen level detected. High risk of nutrient deficiency.")
        if ph < 5.5: auto_alerts.append("Severe Acidic Soil condition found. Nutrient absorption may be blocked.")
        if rain < 100: auto_alerts.append("Drought Risk: Low regional rainfall index recorded.")
        
        result_data = {
            'scenario': scenario,
            'predicted_crop': predicted_crop,
            'auto_alerts': auto_alerts,
            'inputs': {'N': N, 'P': P, 'K': K, 'temperature': temp, 'humidity': humid, 'ph': ph, 'rainfall': rain}
        }
        
        if scenario == '2':
            target_crop = request.form.get('target_crop', '').capitalize()
            result_data['target_crop'] = target_crop
            if target_crop == predicted_crop:
                result_data['suitability'] = "Optimal Compatibility"
                result_data['suitability_desc'] = "Current soil and climate match this crop perfectly for maximum yield potential."
            else:
                result_data['suitability'] = "Sub-Optimal Matrix Detected"
                result_data['suitability_desc'] = f"The environment is better tailored for '{predicted_crop}'. Cultivating '{target_crop}' may cause low yields."
                
        elif scenario == '3':
            # Scenario 3 acts as the master aggregation panel for researchers
            policies = []
            if N < 40: policies.append("Initiate immediate regional N-fertilizer subsidies.")
            if ph < 5.5: policies.append("Deploy administrative lime distribution programs to stabilize pH levels.")
            if rain < 100: policies.append("Fund local micro-irrigation system infrastructure.")
            if not policies: policies.append("Environment stable. Endorse standard crop rotation schedules.")
            result_data['policy_recommendations'] = policies

        return render_template('result.html', result=result_data)
        
    except ValueError as val_error:
        return render_template('index.html', error=str(val_error))
    except Exception as e:
        return render_template('index.html', error="An internal system error occurred.")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
