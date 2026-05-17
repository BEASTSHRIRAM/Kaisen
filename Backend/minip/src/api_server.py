"""
REST API Server for Kaisen Frontend
Serves collected metrics, alerts, and attack graph data with WebSocket support
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import os
from pathlib import Path
import threading
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access
socketio = SocketIO(app, cors_allowed_origins="*")  # WebSocket support

# Paths to data files
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / 'logs'
HISTORY_FILE = LOGS_DIR / 'history.json'
ALERTS_FILE = LOGS_DIR / 'alerts.json'
GRAPH_FILE = LOGS_DIR / 'collected_graph.json'


def read_json_file(filepath, default=None):
    """Read JSON file with error handling"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return default if default is not None else []
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return default if default is not None else []


@app.route('/api/metrics/latest', methods=['GET'])
def get_latest_metrics():
    """Get the most recent system metrics"""
    history = read_json_file(HISTORY_FILE, [])
    if history:
        return jsonify(history[-1])
    return jsonify({
        "cpu_usage": 0,
        "memory_usage": 0,
        "process_count": 0,
        "network_connections": 0,
        "failed_logins": 0,
        "unique_ip_count": 0,
        "timestamp": "",
        "node_id": "unknown",
        "anomaly_score": 0
    })


@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get all alerts"""
    alerts = read_json_file(ALERTS_FILE, [])
    
    # Apply filters if provided
    severity = request.args.get('severity')
    limit = request.args.get('limit', type=int)
    
    if severity:
        alerts = [a for a in alerts if a.get('severity') == severity]
    
    # Sort by timestamp (newest first)
    alerts = sorted(alerts, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    if limit:
        alerts = alerts[:limit]
    
    return jsonify(alerts)


@app.route('/api/graph', methods=['GET'])
def get_attack_graph():
    """Get the attack graph"""
    graph = read_json_file(GRAPH_FILE, {
        "nodes": [],
        "edges": [],
        "metadata": {
            "generated_at": "",
            "node_count": 0,
            "edge_count": 0
        }
    })
    return jsonify(graph)


@app.route('/api/suspicious-ips', methods=['GET'])
def get_suspicious_ips():
    """Get suspicious IP addresses from alerts"""
    alerts = read_json_file(ALERTS_FILE, [])
    
    # Extract unique suspicious IPs
    ip_data = {}
    for alert in alerts:
        for ip in alert.get('suspicious_ips', []):
            if ip not in ip_data:
                ip_data[ip] = {
                    "ip": ip,
                    "connection_count": 0,
                    "failed_attempts": 0,
                    "risk_score": 0,
                    "last_seen": alert.get('timestamp', ''),
                    "node_id": alert.get('node_id', '')
                }
            ip_data[ip]['connection_count'] += 1
            ip_data[ip]['risk_score'] = max(ip_data[ip]['risk_score'], alert.get('anomaly_score', 0))
            if alert.get('timestamp', '') > ip_data[ip]['last_seen']:
                ip_data[ip]['last_seen'] = alert.get('timestamp', '')
    
    return jsonify(list(ip_data.values()))


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get historical metrics"""
    limit = request.args.get('limit', default=100, type=int)
    history = read_json_file(HISTORY_FILE, [])
    
    # Return most recent entries
    return jsonify(history[-limit:] if len(history) > limit else history)


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    history = read_json_file(HISTORY_FILE, [])
    alerts = read_json_file(ALERTS_FILE, [])
    
    stats = {
        "total_collections": len(history),
        "total_alerts": len(alerts),
        "critical_alerts": len([a for a in alerts if a.get('severity') == 'critical']),
        "high_alerts": len([a for a in alerts if a.get('severity') == 'high']),
        "medium_alerts": len([a for a in alerts if a.get('severity') == 'medium']),
        "low_alerts": len([a for a in alerts if a.get('severity') == 'low']),
    }
    
    if history:
        latest = history[-1]
        stats.update({
            "current_cpu": latest.get('cpu_usage', 0),
            "current_memory": latest.get('memory_usage', 0),
            "current_processes": latest.get('process_count', 0),
            "current_connections": latest.get('network_connections', 0),
        })
    
    return jsonify(stats)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "kaisen-api"})


# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    emit('connection_response', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')


# Background thread to watch for file changes and emit updates
def watch_files():
    """Watch log files for changes and emit updates via WebSocket"""
    last_history_size = 0
    last_alerts_size = 0
    
    while True:
        try:
            # Check history file for new metrics
            if os.path.exists(HISTORY_FILE):
                current_size = os.path.getsize(HISTORY_FILE)
                if current_size != last_history_size:
                    last_history_size = current_size
                    history = read_json_file(HISTORY_FILE, [])
                    if history:
                        latest_metrics = history[-1]
                        socketio.emit('metrics', latest_metrics)
                        print(f"Emitted metrics update: {latest_metrics.get('timestamp')}")
            
            # Check alerts file for new alerts
            if os.path.exists(ALERTS_FILE):
                current_size = os.path.getsize(ALERTS_FILE)
                if current_size != last_alerts_size:
                    last_alerts_size = current_size
                    alerts = read_json_file(ALERTS_FILE, [])
                    if alerts:
                        latest_alert = alerts[-1]
                        socketio.emit('alert', latest_alert)
                        print(f"Emitted alert: {latest_alert.get('alert_id')}")
            
            time.sleep(1)  # Check every second for real-time updates
            
        except Exception as e:
            print(f"Error in file watcher: {e}")
            time.sleep(5)


if __name__ == '__main__':
    print("Starting Kaisen API Server...")
    print(f"Logs directory: {LOGS_DIR}")
    print("API endpoints:")
    print("  GET /api/metrics/latest")
    print("  GET /api/alerts")
    print("  GET /api/graph")
    print("  GET /api/suspicious-ips")
    print("  GET /api/history")
    print("  GET /api/stats")
    print("  GET /api/health")
    print("\nWebSocket events:")
    print("  connect - Client connection")
    print("  disconnect - Client disconnection")
    print("  metrics - Real-time metrics updates")
    print("  alert - Real-time alert notifications")
    print("\nServer running on http://localhost:8000")
    
    # Start file watcher thread
    watcher_thread = threading.Thread(target=watch_files, daemon=True)
    watcher_thread.start()
    
    # Run with SocketIO
    socketio.run(app, host='0.0.0.0', port=8000, debug=True, allow_unsafe_werkzeug=True)
