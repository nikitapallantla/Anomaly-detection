import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

def produce_final_report():
    print("📊 Loading audit results for final analysis...")
    
    results = []
    # Read the JSONL file line by line
    with open("audit_results.jsonl", "r", encoding='utf-8') as f:
        for line in f:
            try:
                results.append(json.loads(line))
            except: continue

    df = pd.DataFrame(results)
    
    # 1. Calculate Metrics
    # Ensure we only compare rows that actually have both values
    df = df.dropna(subset=['actual', 'pred'])
    
    y_true = df['actual']
    y_pred = df['pred']
    
    acc = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred)

    print("-" * 30)
    print(f"✅ FINAL ACCURACY: {acc*100:.2f}%")
    print("-" * 30)
    print("Detailed Classification Report:")
    print(report)

    # 2. Visualization: Anomaly Type Distribution
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    
    # Compare Actual vs Predicted counts
    plot_data = df.melt(value_vars=['actual', 'pred'], var_name='Source', value_name='Type')
    ax = sns.countplot(data=plot_data, x='Type', hue='Source', palette='viridis')
    
    plt.title(f"System Audit: AI Prediction vs. Ground Truth\nOverall Accuracy: {acc*100:.2f}%", fontsize=14)
    plt.ylabel("Count of Traces")
    plt.xlabel("Anomaly Category")
    
    # Save the chart for your report
    plt.savefig("anomaly_detection_performance.png")
    print("\n📈 Visualization saved as 'anomaly_detection_performance.png'")

if __name__ == "__main__":
    produce_final_report()