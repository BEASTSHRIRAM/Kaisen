#!/usr/bin/env python3
"""
KAISEN Dashboard Simulator: Generate real-time alerts and metrics
Simulates attacks and feeds them to the Kaisen API for visualization
Run alongside: python eval/demo_dashboard_simulator.py
"""

import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Paths
BACKEND_MINIP = Path(__file__).parent.parent / 'Backend' / 'minip'
LOGS_DIR = BACKEND_MINIP / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

HISTORY_FILE = LOGS_DIR / 'history.json'
ALERTS_FILE = LOGS_DIR / 'alerts.json'
GRAPH_FILE = LOGS_DIR / 'collected_graph.json'

# Initialize files
HISTORY_FILE.write_text('[]')
ALERTS_FILE.write_text('[]')


def generate_timestamp():
    """Generate current timestamp in ISO format"""
    return datetime.now().isoformat()


def generate_benign_metrics():
    """Generate normal system metrics"""
    return {
        "cpu_usage": random.uniform(10, 30),
        "memory_usage": random.uniform(40, 70),
        "process_count": random.randint(20, 40),
        "network_connections": random.randint(5, 15),
        "unique_ip_count": random.randint(2, 5),
        "failed_logins": random.randint(0, 2),
        "lateral_movement_score": random.uniform(0, 0.2),
        "port_scan_score": random.uniform(0, 0.1),
        "resource_exhaustion_score": random.uniform(0, 0.3),
        "entropy_score": random.uniform(1, 3),
        "anomaly_score": random.uniform(0, 0.2),
        "timestamp": generate_timestamp(),
        "node_id": "host-001",
    }


def generate_attack_metrics(attack_type="synchronized"):
    """Generate suspicious metrics for different attack types"""
    
    if attack_type == "synchronized":
        return {
            "cpu_usage": random.uniform(40, 70),
            "memory_usage": random.uniform(70, 90),
            "process_count": random.randint(60, 100),
            "network_connections": random.randint(50, 100),
            "unique_ip_count": random.randint(15, 30),
            "failed_logins": random.randint(10, 20),
            "lateral_movement_score": random.uniform(0.7, 0.95),
            "port_scan_score": random.uniform(0.6, 0.95),
            "resource_exhaustion_score": random.uniform(0.6, 0.95),
            "entropy_score": random.uniform(5, 8),
            "anomaly_score": random.uniform(0.7, 0.95),
            "timestamp": generate_timestamp(),
            "node_id": "host-001",
        }
    elif attack_type == "dos":
        return {
            "cpu_usage": random.uniform(85, 99),
            "memory_usage": random.uniform(85, 99),
            "process_count": random.randint(150, 250),
            "network_connections": random.randint(200, 500),
            "unique_ip_count": random.randint(50, 100),
            "failed_logins": 0,
            "lateral_movement_score": 0,
            "port_scan_score": 0.1,
            "resource_exhaustion_score": random.uniform(0.9, 0.99),
            "entropy_score": random.uniform(7, 9),
            "anomaly_score": random.uniform(0.85, 0.99),
            "timestamp": generate_timestamp(),
            "node_id": "host-001",
        }
    else:  # port_scan
        return {
            "cpu_usage": random.uniform(20, 40),
            "memory_usage": random.uniform(45, 65),
            "process_count": random.randint(25, 45),
            "network_connections": random.randint(100, 200),
            "unique_ip_count": random.randint(30, 60),
            "failed_logins": random.randint(5, 10),
            "lateral_movement_score": random.uniform(0.3, 0.6),
            "port_scan_score": random.uniform(0.8, 0.98),
            "resource_exhaustion_score": random.uniform(0.1, 0.4),
            "entropy_score": random.uniform(4, 6),
            "anomaly_score": random.uniform(0.6, 0.85),
            "timestamp": generate_timestamp(),
            "node_id": "host-001",
        }


def generate_alert(attack_type, anomaly_score):
    """Generate an alert object"""
    
    alert_types = {
        "synchronized": {
            "title": "🔴 SYNCHRONIZED ATTACK DETECTED",
            "description": "Coordinated OS + LLM-layer compromise detected",
            "severity": "critical",
            "indicators": [
                "Lateral movement detected (OS layer)",
                "Jailbreak attempt detected (agent layer)",
                "Privilege escalation attempt",
                "Data exfiltration signals",
            ]
        },
        "dos": {
            "title": "🟠 DENIAL OF SERVICE ATTACK",
            "description": "Resource exhaustion attack in progress",
            "severity": "high",
            "indicators": [
                "CPU > 85%",
                "Memory > 85%",
                "Network connections > 200",
                "Flood detected from multiple IPs",
            ]
        },
        "port_scan": {
            "title": "🟡 RECONNAISSANCE ACTIVITY",
            "description": "Port scanning detected on network",
            "severity": "high",
            "indicators": [
                "Port scan detected",
                "Multiple connection attempts",
                "Failed login attempts",
                "Unusual network pattern",
            ]
        }
    }
    
    attack_info = alert_types.get(attack_type, alert_types["synchronized"])
    
    # Generate suspicious IPs
    suspicious_ips = [f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}" for _ in range(3)]
    
    return {
        "alert_id": f"ALT-{int(time.time()*1000) % 100000:05d}",
        "title": attack_info["title"],
        "description": attack_info["description"],
        "severity": attack_info["severity"],
        "anomaly_score": round(anomaly_score, 3),
        "timestamp": generate_timestamp(),
        "node_id": "host-001",
        "suspicious_ips": suspicious_ips,
        "indicators": attack_info["indicators"],
        "recommended_action": "BLOCK & INVESTIGATE",
        "confidence": round(anomaly_score * 100, 1),
    }


def save_json(filepath, data):
    """Save data to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def append_alert(alert):
    """Append alert to alerts file"""
    try:
        alerts = json.loads(ALERTS_FILE.read_text()) if ALERTS_FILE.exists() else []
    except:
        alerts = []
    
    alerts.append(alert)
    save_json(ALERTS_FILE, alerts[-100:])  # Keep last 100 alerts


def append_metric(metric):
    """Append metric to history file"""
    try:
        history = json.loads(HISTORY_FILE.read_text()) if HISTORY_FILE.exists() else []
    except:
        history = []
    
    history.append(metric)
    save_json(HISTORY_FILE, history[-500:])  # Keep last 500 metrics


def run_simulator():
    """Main simulator loop"""
    
    print("\n" + "="*70)
    print("📊 KAISEN Dashboard Simulator - Real-time Alert Generator")
    print("="*70)
    print(f"\n[+] Logs directory: {LOGS_DIR}")
    print(f"[+] History file: {HISTORY_FILE}")
    print(f"[+] Alerts file: {ALERTS_FILE}")
    
    print("\n[*] Starting attack simulation...")
    print("    Scenario: Alternating benign → synchronized attack → DoS → port scan")
    print("    Updates every 2 seconds")
    print("    Press Ctrl+C to stop\n")
    
    # Simulation parameters
    cycle_count = 0
    benign_counter = 0
    attack_counter = 0
    
    try:
        while True:
            cycle_count += 1
            
            # Cycle through scenarios
            if cycle_count % 10 == 1:
                # Start with 2 seconds of benign behavior
                scenario = "benign"
                benign_counter += 1
                anomaly_score = random.uniform(0.05, 0.2)
            elif cycle_count % 10 <= 3:
                # Synchronized attack for 6 seconds
                scenario = "synchronized"
                attack_counter += 1
                anomaly_score = random.uniform(0.75, 0.95)
            elif cycle_count % 10 <= 5:
                # DoS attack for 4 seconds
                scenario = "dos"
                attack_counter += 1
                anomaly_score = random.uniform(0.8, 0.99)
            else:
                # Port scan for 4 seconds
                scenario = "port_scan"
                attack_counter += 1
                anomaly_score = random.uniform(0.65, 0.85)
            
            # Generate data
            if scenario == "benign":
                metric = generate_benign_metrics()
            else:
                metric = generate_attack_metrics(scenario)
            
            # Append metric
            append_metric(metric)
            
            # Generate and append alert if attack
            if scenario != "benign":
                alert = generate_alert(scenario, anomaly_score)
                append_alert(alert)
                
                # Print alert
                severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                emoji = severity_emoji.get(alert["severity"], "❓")
                print(f"{emoji} [{cycle_count:3d}] {alert['title']:<40} Score: {anomaly_score:.3f}")
            else:
                # Print benign metrics
                print(f"🟢 [{cycle_count:3d}] Normal operation - CPU: {metric['cpu_usage']:.1f}% | MEM: {metric['memory_usage']:.1f}%")
            
            time.sleep(2)  # Update every 2 seconds
            
    except KeyboardInterrupt:
        print("\n\n[*] Simulator stopped")
        print(f"    Generated {benign_counter} benign cycles")
        print(f"    Generated {attack_counter} attack cycles")
        print(f"    Total cycles: {cycle_count}")


if __name__ == '__main__':
    run_simulator()
