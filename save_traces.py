import requests
import json
import os

# 1. Define the destination
FOLDER_PATH = r"C:\Users\nikit\OneDrive\Desktop\Anomaly-1"
FILE_NAME = "final_trace_list_1500.json"
FULL_PATH = os.path.join(FOLDER_PATH, FILE_NAME)

# 2. Query Jaeger (Adjust limit to match your total)
JAEGER_URL = "http://localhost:16686/api/traces?service=api-gateway&limit=1500"

print(f"📡 Exporting traces from Jaeger...")

try:
    response = requests.get(JAEGER_URL)
    if response.status_code == 200:
        data = response.json()
        
        # 3. Write to the folder
        with open(FULL_PATH, "w") as f:
            json.dump(data, f, indent=4)
            
        print(f"✅ SUCCESS!")
        print(f"📁 File saved to: {FULL_PATH}")
        print(f"📊 Total traces exported: {len(data['data'])}")
    else:
        print(f"❌ Failed. Is Jaeger running at localhost:16686?")
except Exception as e:
    print(f"❌ Error: {e}")