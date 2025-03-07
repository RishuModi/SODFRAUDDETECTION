import networkx as nx
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from flask import Flask, request, jsonify
import json
import os
import requests

# Attempt to import Kafka (Handles NoBrokersAvailable error)
try:
    from kafka import KafkaProducer
    kafka_enabled = True
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
except Exception as e:
    print(f"⚠️ Kafka not available: {e}")
    kafka_enabled = False

# Step 1: Read Excel & Detect Conflicts
def detect_conflicts_from_excel(file_path):
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        return {"error": f"Failed to read Excel file: {str(e)}"}

    G = nx.DiGraph()

    # Add nodes and edges from the Excel file
    for _, row in df.iterrows():
        user, role, action = row['User'], row['Role'], row['Action']
        G.add_edge(role, action)
        G.add_edge(user, role)

    # Detect conflicts
    conflicts = []
    for user in set(df['User']):
        roles = list(G.successors(user))
        actions = {action for role in roles for action in G.successors(role)}

        # Conflict if a user has both "Invoice_Creation" and "Payment_Processing"
        if "Invoice_Creation" in actions and "Payment_Processing" in actions:
            conflicts.append(user)

    return conflicts

# Step 2: Machine Learning-Based Fraud Detection
def anomaly_detection_from_excel(file_path):
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        return {"error": f"Failed to read Excel file: {str(e)}"}

    if df.empty:
        return {"error": "Excel file is empty."}

    # Convert categorical roles/actions into numerical values (Feature Encoding)
    df_encoded = pd.get_dummies(df[['Role', 'Action']])

    if df_encoded.empty:
        return {"error": "No valid columns for ML processing."}

    # Use Isolation Forest to detect anomalies
    clf = IsolationForest(contamination=0.1, random_state=42)
    clf.fit(df_encoded)
    predictions = clf.predict(df_encoded)

    # Convert to fraud probability (1 = normal, -1 = anomaly)
    fraud_scores = [round(((1 - p) / 2) * 100, 2) for p in predictions]  # Normalized 0-100 scale

    return fraud_scores

# Step 3: Send Alerts via Kafka
def send_alert(user):
    if kafka_enabled:
        message = {"alert": f"Conflict detected for {user}"}
        producer.send('sod_alerts', json.dumps(message).encode('utf-8'))
    else:
        print(f"⚠️ Kafka is disabled. Alert not sent for {user}.")

# Step 4: Policy Enforcement
def check_policy(user_role):
    policy = {
        "Procurement_Manager": "DENY",
        "Accounts_Payable_Supervisor": "DENY"
    }
    return policy.get(user_role, "ALLOW")

# Step 5: Flask API
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the SoD Fraud Detection API!",
        "routes": {
            "/check_sod": "POST - Upload Excel and check for conflicts & anomalies",
            "/enforce_policy": "POST - Enforce policy based on user role"
        }
    })

@app.route('/check_sod', methods=['POST'])
def check_sod():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    file_path = "uploaded_data.xlsx"
    
    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({"error": f"Failed to save uploaded file: {str(e)}"}), 500

    conflicts = detect_conflicts_from_excel(file_path)
    fraud_scores = anomaly_detection_from_excel(file_path)

    if isinstance(conflicts, dict) or isinstance(fraud_scores, dict):  # If error messages exist
        return jsonify({"error": "Failed to process file", "conflicts": conflicts, "fraud_probabilities": fraud_scores}), 500

    # Send alerts for conflicts
    for user in conflicts:
        send_alert(user)

    # Delete file after processing
    os.remove(file_path)

    return jsonify({
        "conflicts": conflicts,
        "fraud_probabilities": fraud_scores
    })

@app.route('/enforce_policy', methods=['POST'])
def enforce_policy():
    data = request.json
    if not data or "role" not in data:
        return jsonify({"error": "Missing 'role' in request body"}), 400

    decision = check_policy(data["role"])
    return jsonify({"role": data["role"], "decision": decision})

if __name__ == '__main__':
    app.run(debug=True)

# Test API with a POST request
import requests

url = "http://127.0.0.1:5000/check_sod"

# Path to your Excel file
file_path = "C:\\Users\\sahil\\Downloads\\test_sod.xlsx"

try:
    with open(file_path, "rb") as file:
        response = requests.post(url, files={"file": file})
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print(f"Error {response.status_code}: {response.text}")

except requests.exceptions.RequestException as e:
    print("Request failed:", e)

except FileNotFoundError:
    print("Error: Excel file not found! Check the file path.")

except Exception as e:
    print("Unexpected error:", e)
