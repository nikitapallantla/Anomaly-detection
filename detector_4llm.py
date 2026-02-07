import pandas as pd
import os
import time
import json
import google.generativeai as genai # Or use openai

# Configure LLM (Example using Gemini)
genai.configure(api_key="AIzaSyDAHqDQ1UA08k3qn_e76Yw5VVoMdwS-PVY")
model = genai.GenerativeModel('gemini-pro')

def get_llm_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def run_4_llm_analysis(trace_id, logs, metrics, spans):
    # LLM 1: TRACE SPECIALIST
    trace_prompt = f"Analyze these Jaeger spans for Trace {trace_id}. Look for loops or service bottlenecks: {spans}"
    trace_report = get_llm_response(trace_prompt)

    # LLM 2: METRIC SPECIALIST
    metric_prompt = f"Analyze these Prometheus metrics. Look for CPU/Memory spikes during Trace {trace_id}: {metrics}"
    metric_report = get_llm_response(metric_prompt)

    # LLM 3: LOG SPECIALIST
    log_prompt = f"Analyze these actual logs for Trace {trace_id}. Look for 'Failed Login', 'Unauthorized', or 'Brute Force': {logs}"
    log_report = get_llm_response(log_prompt)

    # LLM 4: SUPERVISOR (FINAL VERDICT)
    final_prompt = f"""
    You are a Multimodal Security Supervisor. Review these reports:
    - Traces: {trace_report}
    - Metrics: {metric_report}
    - Logs: {log_report}
    
    Final Task: Correlate all three. If Logs show failed logins and Metrics show high CPU, it's a Brute Force attack.
    Output JSON: {{"verdict": "ANOMALY/NORMAL", "type": "Attack Name", "accuracy": 0.95, "reason": "summary"}}
    """
    return get_llm_response(final_prompt)

def save_to_dataset(data):
    # Fix for issue #2: Ensures results are always appended and saved
    df = pd.DataFrame([data])
    df.to_csv('final_dataset.csv', mode='a', header=not os.path.exists('final_dataset.csv'), index=False)   