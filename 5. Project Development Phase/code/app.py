import os
import pickle
import numpy as np
from flask import Flask, render_template, request

app = Flask(__name__)
MODEL_PATH = os.path.join('models', 'best_crop_model.pkl')

if os.path.exists(MODEL_PATH):
    try:
        with open(MODEL_PATH, 'rb') as f:
            ld = pickle.load(f)
            model = ld.get('model', ld) if isinstance(ld, dict) else ld
    except Exception:
        model = None
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
        ph = float(request.form.get('soil_pH', 0))
        rain = float(request.form.get('rainfall_index', 0))
        
        if model is not None:
            fv = np.array([[N, P, K, temp, humid, ph, rain]])
            raw_pred = model.predict(fv)
            predicted_crop = str(raw_pred).replace('[', '').replace(']', '').replace("'", "").replace('"', '').strip().capitalize()
        else:
            if rain > 150: predicted_crop = "Rice"
            elif N > 100: predicted_crop = "Cotton"
            else: predicted_crop = "Maize"
        
        result_data = {
            'scenario': scenario,
            'predicted_crop': predicted_crop,
            'inputs': {'N': N, 'P': P, 'K': K, 'temperature': temp, 'humidity': humid, 'ph': ph, 'rainfall': rain}
        }
        
        target_crop = request.form.get('target_crop', 'Rice').strip().capitalize()
        result_data['target_crop'] = target_crop
        
        crop_baselines = {
            'Rice': {'N': 80, 'P': 40, 'K': 40, 'ph': (5.5, 6.5), 'temp': (20, 27), 'rain': (150, 250)},
            'Maize': {'N': 60, 'P': 50, 'K': 40, 'ph': (5.8, 7.0), 'temp': (18, 30), 'rain': (60, 110)},
            'Banana': {'N': 100, 'P': 80, 'K': 50, 'ph': (5.5, 6.5), 'temp': (25, 28), 'rain': (90, 115)}
        }
        
        base = crop_baselines.get(target_crop, {'N': 50, 'P': 45, 'K': 35, 'ph': (6.0, 7.0), 'temp': (20, 28), 'rain': (80, 150)})
        reasons_failed = []
        precautions = []
        
        if N < base['N']:
            reasons_failed.append(f"Nitrogen deficit detected ({int(base['N'] - N)} mg/kg below baseline).")
            precautions.append("Incorporate standard urea compounds or nitrogen-rich bio-compost to improve topsoil values.")
        if P < base['P']:
            reasons_failed.append(f"Phosphorus deficit detected ({int(base['P'] - P)} mg/kg below baseline).")
            precautions.append("Apply rock phosphate amendments or bone meal mixtures before planting.")
        if ph < base['ph'][0]:
            reasons_failed.append("Soil acidity level tracks below the critical threshold for this variety.")
            precautions.append("Spread pulverized agricultural lime evenly across fields to raise the pH level.")
        elif ph > base['ph'][1]:
            reasons_failed.append("Soil alkalinity level exceeds the recommended threshold for this variety.")
            precautions.append("Blend organic peat moss or elemental sulfur compounds to restore healthy acidity.")
        if rain < base['rain'][0]:
            reasons_failed.append("Seasonal water index registers below necessary crop irrigation margins.")
            precautions.append("Deploy artificial drip irrigation networks and water-storing hydrogels.")
        elif rain > base['rain'][1]:
            reasons_failed.append("Seasonal water index tracks high, introducing severe root-rot hazards.")
            precautions.append("Construct sub-surface tile drainage channels and build raised cultivation beds.")

        result_data['reasons'] = reasons_failed
        result_data['precautions'] = precautions
        result_data['status'] = "Optimal Match" if not reasons_failed else "Soil Modifications Required"

        if scenario == '3':
            policies = []
            if N < 40 or P < 45 or K < 40:
                policies.append(f"Macro Nutrient Crisis: Regional monitoring data exposes a severe NPK depletion trend, threatening long-term food security for the {target_crop} supply chain. Policymakers must launch an urgent fertilizer credit program and establish specialized cold-storage buffer assets to stabilize local yield output targets.")
            else:
                policies.append(f"Nutrient Stability Assurance: Current regional NPK indicators securely fulfill baseline conditions for {target_crop}. Recommend scaling up export supply channels and provisioning advanced logistics grants to local farming cooperatives.")
                
            if ph < 5.5:
                policies.append(f"Soil Acidification Threat Assessment: Widespread soil mapping signals critical acidification across sub-districts, causing active chemical locks that prevent root absorption. Propose an emergency public procurement project to distribute pulverized agricultural lime and construct regional digital soil testing centers.")
            else:
                policies.append(f"Chemical Neutrality Management: Regional pH structures line up with balanced sustainable matrix guidelines. Authorize routine conservation monitoring to prevent erosion.")
                
            if rain < base['rain'][0]:
                policies.append(f"Severe Arid Hydrological Risk: Local meteorological arrays record a prolonged water deficiency baseline, rendering dryland {target_crop} farming highly vulnerable. Recommend prioritizing public capital outlays toward micro-drip networks, sub-surface aquifer recharge structures, and drought-tolerant seed breeding research.")
            else:
                policies.append(f"Macro Climate Stability Clearance: Seasonal weather data matches natural crop survival margins. Endorse regular crop rotation patterns to lock in soil organic matters.")

            result_data['policy_recommendations'] = policies

        return render_template('result.html', result=result_data)
    except Exception as e:
        return render_template('index.html', error=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
