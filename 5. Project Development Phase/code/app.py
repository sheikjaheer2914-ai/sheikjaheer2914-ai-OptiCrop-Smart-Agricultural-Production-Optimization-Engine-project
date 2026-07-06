import os, pickle
import numpy as np
from flask import Flask, render_template, request

app = Flask(__name__)
MODEL_PATH = os.path.join('models', 'best_crop_model.pkl')

if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f).get('model')
else:
    model = None

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        scenario = request.form.get('scenario', '1')
        N = float(request.form.get('N', 0))
        P = float(request.form.get('P', 0))
        K = float(request.form.get('K', 0))
        temp = float(request.form.get('temperature', 0))
        humid = float(request.form.get('humidity', 0))
        ph = float(request.form.get('ph', 0))
        rain = float(request.form.get('rainfall', 0))
        
        feature_vector = np.array([[N, P, K, temp, humid, ph, rain]])
        raw_prediction = model.predict(feature_vector)
        
        # --- ABSOLUTE FIX: FORCE FULL STRIPPING OF LIST BRACKETS AND QUOTES ---
        predicted_crop = str(raw_prediction).replace('[', '').replace(']', '').replace("'", "").replace('"', '').strip().capitalize()
        
        result_data = {
            'scenario': scenario,
            'predicted_crop': predicted_crop,
            'inputs': {'N': N, 'P': P, 'K': K, 'temperature': temp, 'humidity': humid, 'ph': ph, 'rainfall': rain}
        }
        
        if scenario == '2':
            target_crop = request.form.get('target_crop', '').strip().capitalize()
            result_data['target_crop'] = target_crop
            if target_crop == predicted_crop:
                result_data['status'] = "Optimal Compatibility Match"
                result_data['suitability_desc'] = f"The soil and climate properties align flawlessly for maximum production output yields of {target_crop}."
            else:
                result_data['status'] = "Sub-Optimal Metric Conflict Detected"
                result_data['suitability_desc'] = f"The environment naturally favors '{predicted_crop}'. Cultivating '{target_crop}' presents immediate resource allocation risk."
        elif scenario == '3':
            policies = []
            if N < 40: policies.append("Low Nitrogen recorded: Propose active N-fertilizer resource management subsidies.")
            if ph < 5.5: policies.append("Highly Acidic Profile: Deploy regional lime distribution infrastructure support.")
            if not policies: policies.append("Stable macro metrics verified: Endorse routine soil stabilization rotations.")
            result_data['policy_recommendations'] = policies

        return render_template('result.html', result=result_data)
    except Exception as e:
        return render_template('index.html', error="An engine inference mapping error occurred.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
