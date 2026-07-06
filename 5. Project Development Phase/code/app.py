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
        predicted_crop = str(prediction_output).strip("[]'\"").strip().capitalize()
        
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
            target_crop = request.form.get('target_crop', '').strip().capitalize()
            result_data['target_crop'] = target_crop
            
            crop_baselines = {
                'Rice': {'N': 80, 'P': 40, 'K': 40, 'ph': (5.5, 6.5), 'temp': (20, 27), 'rain': (150, 250)},
                'Maize': {'N': 60, 'P': 50, 'K': 40, 'ph': (5.8, 7.0), 'temp': (18, 30), 'rain': (60, 110)},
                'Pigeonpeas': {'N': 20, 'P': 40, 'K': 20, 'ph': (5.5, 7.5), 'temp': (22, 35), 'rain': (50, 90)},
                'Chickpea': {'N': 30, 'P': 55, 'K': 35, 'ph': (6.0, 7.5), 'temp': (15, 25), 'rain': (40, 70)},
                'Kidneybeans': {'N': 25, 'P': 35, 'K': 22, 'ph': (6.0, 6.8), 'temp': (15, 25), 'rain': (60, 95)},
                'Apple': {'N': 20, 'P': 130, 'K': 140, 'ph': (5.5, 6.5), 'temp': (21, 24), 'rain': (100, 125)},
                'Banana': {'N': 100, 'P': 80, 'K': 50, 'ph': (5.5, 6.5), 'temp': (25, 28), 'rain': (90, 115)}
            }
            
            base = crop_baselines.get(target_crop, {'N': 50, 'P': 45, 'K': 35, 'ph': (6.0, 7.0), 'temp': (20, 28), 'rain': (80, 150)})
            adjustments = []
            climate_clash = False
            
            if N < base['N']: adjustments.append(f"Increase Nitrogen by adding urea or compost (~{int(base['N'] - N)} mg/kg required).")
            if P < base['P']: adjustments.append(f"Boost Phosphorus by applying bone meal (~{int(base['P'] - P)} mg/kg required).")
            if K < base['K']: adjustments.append(f"Raise Potassium levels using muriate of potash (~{int(base['K'] - K)} mg/kg required).")
            if ph < base['ph']: adjustments.append(f"Soil is too acidic. Add agricultural lime to raise the pH level.")
            elif ph > base['ph']: adjustments.append(f"Soil is too alkaline. Treat with elemental sulfur to lower the pH scale.")
                
            if not (base['temp'] <= temp <= base['temp']): climate_clash = True
            if not (base['rain'] <= rain <= base['rain']): climate_clash = True
                
            result_data['adjustments'] = adjustments
            result_data['climate_clash'] = climate_clash
            
            if target_crop == predicted_crop:
                result_data['status'] = "Optimal Compatibility Match"
            elif not climate_clash and adjustments:
                result_data['status'] = "Conditional Suitability Matrix (Modifications Required)"
            else:
                result_data['status'] = "Unachievable Macroclimate Boundary Conflict"
                
        elif scenario == '3':
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
    app.run(host='0.0.0.0', port=5000, debug=True)
