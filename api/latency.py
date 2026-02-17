import json
import numpy as np

def handler(request):
    # Enable CORS
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST",
        "Access-Control-Allow-Headers": "Content-Type"
    }

    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": headers
        }

    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": headers,
            "body": json.dumps({"error": "Only POST allowed"})
        }

    body = json.loads(request.body)
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 0)

    with open("q-vercel-latency.json") as f:
        data = json.load(f)

    result = {}

    for region in regions:
        records = [r for r in data if r["region"] == region]

        if not records:
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(1 for l in latencies if l > threshold)
        }

    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps(result)
    }
