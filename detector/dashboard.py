from flask import Flask, render_template_string
import json
import os

app = Flask(__name__)

# Template is AI generated, refreshes every 3 seconds
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>HNG Anomaly Dashboard</title>
    <meta http-equiv="refresh" content="3">
    <style>
        body { font-family: sans-serif; background: #1a1a1a; color: #eee; padding: 20px; }
        .card { background: #2a2a2a; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 5px solid #007bff; }
        .banned { color: #ff4d4d; font-weight: bold; }
        .metric { font-size: 2em; color: #007bff; }
    </style>
</head>
<body>
    <h1> Anomaly Detection Live Metrics</h1>
    <div class="card">
        <h3>System Health</h3>
        <p>CPU: {{ stats.cpu_usage }}% | Memory: {{ stats.memory_usage }}% | Uptime: {{ stats.uptime }}s</p>
    </div>
    <div class="card">
        <h3>Traffic Stats</h3>
        <p>Global Rate: <span class="metric">{{ stats.global_rate }} req/min</span></p>
        <p>Current Baseline Mean: {{ "%.2f"|format(stats.mean) }}</p>
    </div>
    <div class="card">
        <h3>Banned IPs</h3>
        <ul>
        {% for ip, data in stats.banned_ips.items() %}
            <li class="banned">{{ ip }} - Unban in {{ ((data.unban_at - now)|int) if data.unban_at != inf else 'PERMANENT' }}s</li>
        {% else %}
            <li>No active bans.</li>
        {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    try:
        with open("stats.json", "r") as f:
            stats = json.load(f)
    except:
        stats = {"global_rate": 0, "banned_ips": {}, "cpu_usage": 0, "memory_usage": 0, "uptime": 0, "mean": 0}
    
    import time
    return render_template_string(HTML_TEMPLATE, stats=stats, now=time.time(), inf=float('inf'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
