import json, uuid, random
from datetime import datetime, timedelta

def generate_professional_telemetry():
    services = [
        "account-service", "api-gateway", "audit-service", 
        "auth-service", "fraud-service", "notification-service", 
        "payment-service", "transaction-service", "user-service"
    ]
    
    start_time = datetime.now()
    handlers = {s: open(f"logs/{s}.log", 'w') for s in services}

    print("🏗️  Building 1,500 Full-Pillar Traces (Logs + Metrics + Traces)...")

    for i in range(1500):
        # --- THE TRACE PILLAR ---
        trace_id = uuid.uuid4().hex
        
        # Determine if this journey has a "Global Anomaly"
        global_issue = random.choice(["none", "system_overload", "security_breach"]) if i % 40 == 0 else "none"

        for s_name in services:
            # --- THE METRIC PILLAR ---
            # Standard metrics for every service call
            latency = random.uniform(10, 150) # ms
            cpu_usage = random.uniform(5, 25) # %
            
            # --- THE LOG PILLAR ---
            msg = f"{s_name} execution successful"
            status = 200

            # Injecting Specific Anomalies
            if global_issue == "system_overload":
                latency += 5000  # Metric Anomaly (Performance)
                cpu_usage += 70  # Metric Anomaly (Resource)
                msg = "Resource exhaustion detected"
            
            if global_issue == "security_breach" and s_name == "auth-service":
                msg = "Multiple failed login attempts detected" # Log Anomaly
                status = 401

            # Build the Multimodal Entry
            entry = {
                "timestamp": (start_time + timedelta(milliseconds=i*100)).isoformat(),
                "trace_id": trace_id,           # TRACE
                "service": s_name,              # LOG metadata
                "message": msg,                 # LOG text
                "status": status,               # METRIC (Success rate)
                "metrics": {                    # METRIC (Performance)
                    "latency_ms": round(latency, 2),
                    "cpu_percent": round(cpu_usage, 2),
                    "mem_mb": random.randint(100, 500)
                }
            }

            handlers[s_name].write(json.dumps(entry) + "\n")

    for h in handlers.values(): h.close()
    print("✅ 1,500 Multimodal Traces Generated.")

generate_professional_telemetry()