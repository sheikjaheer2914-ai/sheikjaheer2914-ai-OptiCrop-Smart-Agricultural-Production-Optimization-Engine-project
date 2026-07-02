import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# ==========================================
# CORE ENGINE LOGIC (Designed by: Jaheer Vali Sheik)
# ==========================================
def optimize_crop_production(n, p, k, temp, humidity, ph, rainfall, targeted_crop=None):
    """
    Analyzes chemical & environmental inputs to calculate soil-crop compatibility.
    Supports Scenario 1 (Discovery) and Scenario 2 (Suitability Assessment).
    """
    # Simulated internal data thresholds for demonstration / research analysis
    crop_database = {
        "rice": {"N": 80, "P": 40, "K": 40, "temp": 25, "hum": 80, "ph": 6.5, "rain": 200},
        "maize": {"N": 100, "P": 50, "K": 30, "temp": 28, "hum": 65, "ph": 6.2, "rain": 100},
        "cotton": {"N": 120, "P": 60, "K": 20, "temp": 30, "hum": 50, "ph": 7.0, "rain": 80}
    }
    
    # SCENARIO 2: Evaluate a specific crop requested by the user
    if targeted_crop:
        crop = targeted_crop.lower()
        if crop in crop_database:
            limits = crop_database[crop]
            # Simple absolute deviation score (Lower score = Higher compatibility)
            score = (abs(n - limits["N"]) + abs(p - limits["P"]) + abs(k - limits["K"]) + 
                     abs(temp - limits["temp"]) + abs(humidity - limits["hum"]) + 
                     abs(ph - limits["ph"]) * 10 + abs(rainfall - limits["rain"]))
            
            suitability = "High" if score < 150 else ("Medium" if score < 300 else "Low")
            return {
                "status": "Success",
                "mode": "Crop Suitability Assessment (Scenario 2)",
                "target_crop": crop.capitalize(),
                "suitability_index": suitability,
                "compatibility_score": round(score, 2),
                "insights": f"Soil evaluation completed for {crop.capitalize()} based on current environmental vectors."
            }
        return {"status": "Error", "message": "Requested crop not found in optimization matrix."}
    
    # SCENARIO 1: Suggest the absolute best crop based on input data array
    best_crop = None
    min_deviation = float('inf')
    
    for crop, limits in crop_database.items():
        score = (abs(n - limits["N"]) + abs(p - limits["P"]) + abs(k - limits["K"]) + 
                 abs(temp - limits["temp"]) + abs(humidity - limits["hum"]) + 
                 abs(ph - limits["ph"]) * 10 + abs(rainfall - limits["rain"]))
        if score < min_deviation:
            min_deviation = score
            best_crop = crop

    return {
        "status": "Success",
        "mode": "Smart Crop Recommendation Engine (Scenario 1)",
        "recommended_crop": best_crop.capitalize(),
        "confidence_rating": "Optimal" if min_deviation < 150 else "Adequate",
        "resource_efficiency_note": "Nitrogen-Phosphorous optimization suggested to maximize yield output."
    }

# ==========================================
# STATIC FRONTEND ROUTES (Maintained by: Kiran Ram Kumar)
# ==========================================
@app.route('/')
def home():
    # Serves the static UI shell built by Kiran
    return """
    <html>
        <head><title>OptiCrop Engine</title></head>
        <body style="font-family: Arial, sans-serif; margin: 40px; background-color: #f4f6f9;">
            <h2>OptiCrop: Smart Agricultural Production Optimization Engine</h2>
            <p><strong>Team ID:</strong> SWTID-2026-5396 | <strong>Lead:</strong> Yeswanth Satya Prasad Voleti</p>
            <hr/>
            <h3>Submit Soil & Environmental Data Parameters</h3>
            <form action="/predict" method="POST">
                <label>Nitrogen (N):</label> <input type="number" name="N" required><br><br>
                <label>Phosphorous (P):</label> <input type="number" name="P" required><br><br>
                <label>Potassium (K):</label> <input type="number" name="K" required><br><br>
                <label>Temperature (°C):</label> <input type="number" step="any" name="temperature" required><br><br>
                <label>Humidity (%):</label> <input type="number" step="any" name="humidity" required><br><br>
                <label>pH Level:</label> <input type="number" step="any" name="ph" required><br><br>
                <label>Rainfall (mm):</label> <input type="number" step="any" name="rainfall" required><br><br>
                <label>Target Crop (Optional - Scenario 2):</label> <input type="text" name="crop"><br><br>
                <button type="submit" style="padding: 10px 20px; background-color: #2e7d32; color: white; border: none; cursor: pointer;">Run Optimization Engine</button>
            </form>
        </body>
    </html>
    """

# ==========================================
# CORE API ROUTE (Scenario 1 & 2 Execution)
# ==========================================
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Collect parameters sent via form or raw JSON
        n = float(request.form.get('N', 0))
        p = float(request.form.get('P', 0))
        k = float(request.form.get('K', 0))
        temp = float(request.form.get('temperature', 0))
        hum = float(request.form.get('humidity', 0))
        ph = float(request.form.get('ph', 0))
        rain = float(request.form.get('rainfall', 0))
        target_crop = request.form.get('crop', '').strip()

        # Execute optimization routines logic mapped out by Jaheer
        result = optimize_crop_production(n, p, k, temp, hum, ph, rain, target_crop if target_crop else None)
        return jsonify(result)

    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 400

if __name__ == '__main__':
    # Initialized by Team Leader Yeswanth Satya Prasad Voleti
    app.run(debug=True, host='0.0.0.0', port=5000)
