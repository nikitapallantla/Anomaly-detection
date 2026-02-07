import json, uuid, random, os
from datetime import datetime

def generate_with_ground_truth():
    services = ["account-service", "api-gateway", "audit-service", "auth-service", 
                "fraud-service", "notification-service", "payment-service", 
                "transaction-service", "user-service"]
    
    os.makedirs("logs", exist_ok=True)
    handlers = {s: open(f"logs/{s}.log", 'w') for s in services}
    ground_truth = {} # This is our "Answer Key"

    print("🏗️  Generating 1,500 traces + Ground Truth...")

    for i in range(1500):
        tid = uuid.uuid4().hex
        
        # Decide if this specific trace is an anomaly
        # We'll make ~10% of them anomalies
        is_anomaly = random.random() < 0.10
        anomaly_type = "None"
        
        if is_anomaly:
            anomaly_type = random.choice(["Security", "Performance", "Logic"])
            ground_truth[tid] = {"is_anomaly": True, "type": anomaly_type}
        else:
            ground_truth[tid] = {"is_anomaly": False, "type": "Normal"}

        for s_name in services:
            latency = random.uniform(10, 150)
            msg = "Execution successful"
            status = 200
            
            # Injecting the data for the anomaly we decided on
            if is_anomaly:
                if anomaly_type == "Performance":
                    latency += 5000 # Metric anomaly
                if anomaly_type == "Security" and s_name == "auth-service":
                    status = 401 # Log anomaly
                    msg = "Unauthorized Access"

            entry = {
                "trace_id": tid, "service": s_name, "message": msg, 
                "status": status, "metrics": {"latency_ms": round(latency, 2)}
            }
            handlers[s_name].write(json.dumps(entry) + "\n")

    # Save the Secret Answer Key
    with open("ground_truth.json", "w") as gt_file:
        json.dump(ground_truth, gt_file)

    for h in handlers.values(): h.close()
    print("✅ Logs and ground_truth.json are ready.")

generate_with_ground_truth()