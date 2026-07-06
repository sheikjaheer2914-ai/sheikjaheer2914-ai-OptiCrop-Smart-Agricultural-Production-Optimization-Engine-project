import os
import pickle
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
        raw_pred = model.predict(feature_vector)
        
        # Format ML output vector to strip bracket arrays
        predicted_crop = str(raw_pred).replace('[', '').replace(']', '').replace("'", "").replace('"', '').strip().capitalize()
        
        result_data = {
            'scenario': scenario,
            'predicted_crop': predicted_crop,
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
                'Kidneybeans': {'N': 25, 'P': 35, 'K': 22, 'ph': (6.0, 6.8), 'temp': (15, 25), 'rain': (60, 95)}
            }
            
            base = crop_baselines.get(target_crop, {'N': 50, 'P': 45, 'K': 35, 'ph': (6.0, 7.0), 'temp': (20, 28), 'rain': (80, 150)})
            adjustments = []
            climate_clash = False
            
            if N < base['N']: adjustments.append(f"Add nitrogen fertilizers (~{int(base['N'] - N)} mg/kg required).")
            if P < base['P']: adjustments.append(f"Apply bone meal phosphate composites (~{int(base['P'] - P)} mg/kg required).")
            if K < base['K']: adjustments.append(f"Treat with potassium scaling salts (~{int(base['K'] - K)} mg/kg required).")
            if ph < base['ph']: adjustments.append("Incorporate topsoil lime amendments to reduce ground acidity.")
            elif ph > base['ph']: adjustments.append("Add elemental sulfur minerals to reduce soil alkalinity.")
                
            if not (base['temp'] <= temp <= base['temp']): climate_clash = True
            if not (base['rain'] <= rain <= base['rain']): climate_clash = True
                
            result_data['adjustments'] = adjustments
            result_data['climate_clash'] = climate_clash
            
        elif scenario == '3':
            policies = []
            if N < 40: policies.append("Low Nitrogen recorded: Propose active N-fertilizer subsidies.")
            if ph < 5.5: policies.append("Highly Acidic Profile: Deploy regional lime infrastructure support.")
            if not policies: policies.append("Stable macro metrics verified: Endorse routine soil stabilization rotations.")
            result_data['policy_recommendations'] = policies

        return render_template('result.html', result=result_data)
    except Exception as e:
        return render_template('index.html', error="An engine mapping error occurred.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
