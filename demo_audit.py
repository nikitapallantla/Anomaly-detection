import json, os, time
from google import genai
from google.genai import types 
from dotenv import load_dotenv
from sklearn.metrics import classification_report

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"), http_options=types.HttpOptions(api_version='v1'))

def run_balanced_demo(num_records=20):
    with open("ground_truth.json", "r") as f:
        truth = json.load(f)
    
    # Balance: 7 Performance, 7 Security, 6 Normal
    anoms = [tid for tid, v in truth.items() if v["is_anomaly"]]
    perf = [tid for tid in anoms if truth[tid]["type"] == "Performance"][:7]
    sec = [tid for tid in anoms if truth[tid]["type"] == "Security"][:7]
    norm = [tid for tid, v in truth.items() if not v["is_anomaly"]][:6]
    target_tids = perf + sec + norm
    
    y_true, y_pred = [], []

    for i, tid in enumerate(target_tids):
        actual = truth[tid]["type"]
        y_true.append(actual)

        # Optimization: Only send essential log data to save tokens
        trace_logs = []
        for file in os.listdir("logs"):
            if file.endswith(".log"):
                with open(os.path.join(file_path := os.path.join("logs", file)), "r") as f:
                    for line in f:
                        try:
                            data = json.loads(line)
                            if data.get("trace_id") == tid:
                                # Use .get() to provide defaults and avoid KeyError
                                trace_logs.append({
                                    "s": data.get("service", "unknown"), 
                                    "st": data.get("status_code", 200), # Default to 200 if missing
                                    "l": data.get("latency_ms", 0),
                                    "m": data.get("message", "") # Added message for Logic errors
                                })
                        except json.JSONDecodeError:
                            continue

        prompt = f"Labels: Normal, Security, Performance. Audit logs and return 1 word only. Logs: {json.dumps(trace_logs)}"
        
        success = False
        wait_time = 15 # Start with a 15s gap
        while not success:
            try:
                response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                pred = response.text.strip()
                label = "Performance" if "Perf" in pred else "Security" if "Sec" in pred else "Normal"
                
                y_pred.append(label)
                print(f"[{i+1}/20] Trace {tid[:8]} | Actual: {actual:12} | AI: {label}")
                success = True
                time.sleep(wait_time) 

            except Exception as e:
                if "429" in str(e):
                    print(f"⚠️ Rate limit. Waiting 40s...")
                    time.sleep(40)
                else:
                    print(f"❌ Error: {e}")
                    y_pred.append("Error")
                    success = True

    print("\n" + "="*60 + "\nFINAL SYSTEM AUDIT REPORT\n" + "="*60)
    print(classification_report(y_true, y_pred, zero_division=0))

if __name__ == "__main__":
    run_balanced_demo(20)