import os, pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
df = pd.read_csv("data/crop_recommendation.csv")
X = df[["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]]
y = df["label"]
m = RandomForestClassifier(n_estimators=10, random_state=42).fit(X, y)
os.makedirs("models", exist_ok=True)
with open("models/best_crop_model.pkl", "wb") as f_out: 
    pickle.dump({"model": m}, f_out)
print("Model infrastructure saved.")
