import yaml
import time
import datetime
import json
import psutil
import os
from monitor import LogMonitor
from baseline import BaselineManager
from detector import AnomalyDetector
from notifier import SlackNotifier
from blocker import FirewallBlocker
from unbanner import UnbanManager

# SETUP & INITIALIZATION 
start_time = time.time()
last_recalc = time.time()
AUDIT_FILE = "audit.log"

with open("config.yaml") as f:
    config = yaml.safe_load(f)

monitor = LogMonitor(config["log_file"])
baseline = BaselineManager()
detector = AnomalyDetector(baseline)
notifier = SlackNotifier() 
blocker = FirewallBlocker(config["whitelist"])
unbanner = UnbanManager(blocker, config["ban_schedule"])

# HELPER FUNCTIONS 

def write_audit(action, ip, condition, rate, baseline_val, duration="N/A"):
    """Requirement: Write structured log entries for every ban, unban, and recalibration."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {action} {ip} | {condition} | {rate} | {baseline_val:.2f} | {duration}\n"
    with open(AUDIT_FILE, "a") as f:
        f.write(entry)

def save_stats():
    """Writes system state to JSON for the Live Metrics UI."""
    try:
        m, s = baseline.get_stats()
        stats = {
            "global_rate": len(detector.global_window),
            "banned_ips": unbanner.banned_ips,
            "mean": m,
            "stddev": s,
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "uptime": int(time.time() - start_time)
        }
        with open("stats.json.tmp", "w") as f:
            json.dump(stats, f)
        os.rename("stats.json.tmp", "stats.json")
    except Exception as e:
        print(f"Error saving stats: {e}")

# --- THE ENGINE ---

# Initial audit entry & stats kickstart
write_audit("STARTUP", "SYSTEM", "Engine Initialized", 0, 1.0)
save_stats()

print(" Anomaly Engine is LIVE and learning traffic patterns...")

try:
    for log in monitor.follow():
        print(f"DEBUG: Processing log from {log.get('source_ip')}", flush=True)
        # A. Update Baseline (add 1 request to the hourly slot)
        baseline.update(1) 
        
        # B. Process Log through Detector
        is_anomaly, reason, rate, mean = detector.process_log(log)
        
        # C. Handle IP Anomaly (Requirement: Block + Slack + Audit)
        if is_anomaly:
            ip = log.get('source_ip')
            if blocker.block_ip(ip):
                duration = unbanner.add_ban(ip)
                write_audit("BAN", ip, reason, rate, mean, f"{duration}s")
                
                msg = (f" *BANNED*: `{ip}` for {duration//60} mins\n"
                       f"Reason: {reason}\nRate: {rate} | Baseline: {mean:.2f}")
                print(f"!!! ANOMALY !!! {msg}")
                notifier.send_alert(msg)

        # D. Handle Global Anomaly (Requirement: Slack Alert ONLY)
        global_rate = len(detector.global_window)
        g_mean, g_std = baseline.get_stats()
        if global_rate > (g_mean * 5) and g_mean > 2: # Check threshold
            notifier.send_alert(f"*GLOBAL SPIKE*: {global_rate} req/s! (Baseline: {g_mean:.2f})")
            write_audit("GLOBAL_ALERT", "ALL", "Global Spike", global_rate, g_mean)

        # E. Handle Auto-Unbans
        released = unbanner.check_unbans()
        for ip in released:
            write_audit("UNBAN", ip, "Timer Expired", "N/A", mean)
            notifier.send_alert(f" *UNBANNED*: `{ip}` is allowed back in.")

        # F. Recalculate Baseline every 60 seconds (Requirement)
        if time.time() - last_recalc > 60:
            m, s = baseline.recalculate()
            print(f" [RECALC] New Baseline Mean: {m:.2f} | StdDev: {s:.2f}", flush=True)
            write_audit("RECALC", "SYSTEM", "Rolling Update", m, s)
            last_recalc = time.time()

        # G. Update Dashboard
        save_stats()

except KeyboardInterrupt:
    write_audit("SHUTDOWN", "SYSTEM", "Manual Termination", 0, 0)
    print("\nStopping Anomaly Engine...")
