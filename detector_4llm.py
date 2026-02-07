import os
import json
import pandas as pd
from dotenv import load_dotenv
from google import genai
import time
import glob

# 1. Configuration and API Client Setup
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def throttled_audit(prompt, model="gemini-2.0-flash"):
    """Makes an API call with increased batch-friendly retry logic."""
    max_retries = 5
    retry_delay = 15 

    for attempt in range(max_retries):
        try:
            # Slightly longer sleep to ensure batch stability
            time.sleep(5) 
            response = client.models.generate_content(
                model=model, 
                contents=prompt,
                config={'response_mime_type': 'application/json'} # Force JSON output
            )
            return response.text
        except Exception as e:
            if "429" in str(e):
                wait_time = retry_delay * (2 ** attempt)
                print(f"🕒 Rate limit hit. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"❌ Error: {e}")
                return None
    return "FAILED_AFTER_RETRIES"

def run_large_audit():
    # 1. Automatically grab all 9 service logs from your folder
    log_folder = r"C:\Users\nikit\OneDrive\Desktop\Anomaly -1\logs\*.log"
    log_files = glob.glob(log_folder)
    
    if not log_files:
        print(f"❌ No .log files found in {log_folder}")
        return

    # 2. Correlate logs by Trace ID
    correlated_data = {}

    print(f"📂 Reading {len(log_files)} service logs (Full System Audit)...")
    for file_path in log_files:
        service_name = os.path.basename(file_path).replace(".log", "")
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    tid = entry.get("trace_id")
                    if tid:
                        if tid not in correlated_data:
                            correlated_data[tid] = []
                        entry["service"] = service_name
                        correlated_data[tid].append(entry)
                except: continue

    all_tids = list(correlated_data.keys())
    print(f"📦 Successfully correlated {len(all_tids)} unique Traces across the cluster.")

    # 3. Batch Processing (The FIX for Rate Limits)
    batch_size = 10 
    for i in range(0, len(all_tids), batch_size):
        batch_keys = all_tids[i:i + batch_size]
        batch_payload = []
        
        for tid in batch_keys:
            batch_payload.append({
                "trace_id": tid,
                "data": correlated_data[tid]
            })

        master_prompt = master_prompt = f"""
        Act as a 4-Agent Distributed Systems Auditor.
        Analyze this BATCH of {len(batch_payload)} microservice traces.
        Each trace contains Logs, Metrics (CPU/Latency), and Distributed Trace IDs.

        [BATCH DATA]:
        {json.dumps(batch_payload, indent=2)}

        TASK:
        For EACH trace in the batch, provide a multimodal analysis:
        1. (Log Agent): Search "message" fields for security errors (401, 403, Unauthorized).
        2. (Metric Agent): Analyze the "metrics" object. Flag latency > 1000ms as 'Performance Issue' and CPU > 60% as 'Resource Stress'.
        3. (Trace Agent): Verify the request flow. Does the trace ID appear across all expected services?
        4. (Fusion Agent): Correlate all pillars. Example: "High CPU (Metric) matches a Brute Force attempt (Log)."

        Return ONLY a JSON list of objects:
        [
          {{
            "trace_id": "...", 
            "verdict": "ANOMALY/NORMAL", 
            "anomaly_type": "Security/Performance/Logic",
            "root_cause_service": "...", 
            "reasoning": "Explain using BOTH log text and metric numbers"
          }}
        ]
        """

        print(f"📡 Auditing Batch: {i//batch_size + 1} (Traces {i} to {i+len(batch_keys)})")
        analysis_result = throttled_audit(master_prompt)

        # 4. Save results (Handling the batch response)
        if analysis_result != "FAILED_AFTER_RETRIES":
            try:
                # Append each verdict in the batch to your results file
                verdicts = json.loads(analysis_result)
                with open("audit_results.jsonl", "a", encoding='utf-8') as f:
                    for v in verdicts:
                        f.write(json.dumps(v) + "\n")
            except:
                with open("audit_results.jsonl", "a", encoding='utf-8') as f:
                    f.write(json.dumps({"batch_index": i, "error": "AI_JSON_PARSE_ERROR", "raw": analysis_result}) + "\n")
        else:
            print(f"⚠️ Batch starting at {i} failed after all retries.")

if __name__ == "__main__":
    run_large_audit()