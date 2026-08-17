"""
Start both the log collector and API server together
"""
import sys
import os

# Auto-detect and use local .venv Python if missing dependencies in current interpreter
_backend_dir = os.path.dirname(os.path.abspath(__file__))
_venv_python = os.path.join(_backend_dir, '.venv', 'Scripts', 'python.exe')
if os.path.exists(_venv_python) and os.path.abspath(sys.executable).lower() != os.path.abspath(_venv_python).lower():
    try:
        import networkx
    except ImportError:
        os.execv(_venv_python, [_venv_python] + sys.argv)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import threading
import time


# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from collection_config import CollectionConfig
from log_collector import LogCollector

def run_collector():
    """Run the log collector in continuous mode"""
    print("=" * 60)
    print("  LOG COLLECTOR STARTING")
    print("=" * 60)
    
    # Load configuration
    config = CollectionConfig.from_file("config.json")
    config.setup_logging()
    
    # Create and start collector
    collector = LogCollector(config)
    
    print(f"\n✓ Collector initialized")
    print(f"✓ Collection interval: {config.collection_interval_seconds} seconds")
    print(f"✓ Model loaded: {config.model_path}")
    print(f"✓ Anomaly threshold: {config.anomaly_threshold}")
    print(f"✓ Log directory: {config.log_dir}")
    print("\nStarting continuous collection...\n")
    
    # Start continuous collection
    collector.start()
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping collector...")
        collector.stop()
        print("Collector stopped.")

def run_api_server():
    """Run the Flask API server"""
    print("=" * 60)
    print("  API SERVER STARTING")
    print("=" * 60)
    
    # Import and run the API server
    from api_server import app, socketio, watch_files
    import threading
    
    print("\n✓ API Server initialized")
    print("✓ Endpoints available:")
    print("  - GET /api/metrics/latest")
    print("  - GET /api/alerts")
    print("  - GET /api/graph")
    print("  - GET /api/suspicious-ips")
    print("  - GET /api/history")
    print("  - GET /api/stats")
    print("  - GET /api/health")
    print("\n✓ WebSocket support enabled")
    print("  - Real-time metrics updates")
    print("  - Real-time alert notifications")
    print("\n✓ Server running on http://localhost:8000")
    print("\n")
    
    # Start file watcher thread
    watcher_thread = threading.Thread(target=watch_files, daemon=True)
    watcher_thread.start()
    
    # Run with SocketIO
    socketio.run(app, host='0.0.0.0', port=8000, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    print("\n")
    print("+" + "=" * 58 + "+")
    print("|" + " " * 15 + "KAISEN BACKEND SERVICES" + " " * 20 + "|")
    print("+" + "=" * 58 + "+")
    print("\n")

    
    # Start collector in a separate thread
    collector_thread = threading.Thread(target=run_collector, daemon=True)
    collector_thread.start()
    
    # Give collector a moment to initialize
    time.sleep(2)
    
    # Run API server in main thread (so CTRL+C works properly)
    try:
        run_api_server()
    except KeyboardInterrupt:
        print("\n\nShutting down all services...")
        print("Goodbye!")
