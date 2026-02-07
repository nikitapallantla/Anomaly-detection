import json

def run_final_evaluation():
    # 1. Load the "Answer Key"
    with open("ground_truth.json", "r") as f:
        truth = json.load(f)

    # 2. Load the "AI's Guesses"
    ai_results = {}
    with open("audit_results.jsonl", "r") as f:
        for line in f:
            data = json.loads(line)
            # Check if AI mentioned "ANOMALY" in its text verdict
            ai_results[data["trace_id"]] = "ANOMALY" in data.get("analysis", "").upper()

    tp, fp, tn, fn = 0, 0, 0, 0

    for tid, actual in truth.items():
        predicted = ai_results.get(tid, False)
        is_actual_anomaly = actual["is_anomaly"]

        if predicted and is_actual_anomaly: tp += 1
        elif predicted and not is_actual_anomaly: fp += 1
        elif not predicted and not is_actual_anomaly: tn += 1
        elif not predicted and is_actual_anomaly: fn += 1

    # Calculation
    total = tp + fp + tn + fn
    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    print("="*40)
    print(f"📊 FINAL SYSTEM AUDIT RESULTS")
    print("="*40)
    print(f"✅ Accuracy:  {accuracy:.2%}")
    print(f"🎯 Precision: {precision:.2%}")
    print(f"🔍 Recall:    {recall:.2%}")
    print("-"*40)
    print(f"Total Traces: {total}")
    print(f"Anomalies Caught: {tp} / {tp + fn}")
    print("="*40)

if __name__ == "__main__":
    run_final_evaluation()