import json

def load_metrics():
    try:
        with open("metrics.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"run_count": 0}

def save_metrics(metrics):
    with open("metrics.json", "w") as f:
        json.dump(metrics, f)
