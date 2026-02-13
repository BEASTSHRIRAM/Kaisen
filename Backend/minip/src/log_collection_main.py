#!/usr/bin/env python3
"""
Main entry point for the Kaisen Log Collection Backend.

This module provides a command-line interface for starting log collection,
performing single collections, and exporting attack graphs.

Commands:
    start: Start continuous log collection
    collect-once: Perform a single collection cycle
    export-graph: Export the current attack graph to JSON

Requirements validated:
- 9.1: Read configuration from config file at startup
- 11.1: Integrate with existing Backend/minip/ codebase
"""

import sys
import signal
import argparse
import logging
from pathlib import Path

from src.collection_config import CollectionConfig
from src.log_collector import LogCollector


logger = logging.getLogger(__name__)


class LogCollectionMain:
    """
    Main application class for log collection backend.
    
    Handles command-line argument parsing, configuration loading,
    component initialization, and graceful shutdown.
    """
    
    def __init__(self):
        """Initialize the main application."""
        self.collector: LogCollector = None
        self.config: CollectionConfig = None
        self.running = False
    
    def setup_signal_handlers(self):
        """
        Set up signal handlers for graceful shutdown.
        
        Handles SIGINT (Ctrl+C) and SIGTERM to stop collection cleanly.
        """
        def signal_handler(signum, frame):
            """Handle shutdown signals."""
            signal_name = 'SIGINT' if signum == signal.SIGINT else 'SIGTERM'
            logger.info(f"Received {signal_name}, shutting down gracefully...")
            
            if self.collector and self.running:
                self.collector.stop()
            
            logger.info("Shutdown complete")
            sys.exit(0)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.debug("Signal handlers registered")
    
    def load_configuration(self, config_path: str) -> CollectionConfig:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration JSON file
            
        Returns:
            CollectionConfig instance
        """
        logger.info(f"Loading configuration from: {config_path}")
        config = CollectionConfig.from_file(config_path)
        
        # Setup logging based on configuration
        config.setup_logging()
        
        return config
    
    def initialize_collector(self, config: CollectionConfig) -> LogCollector:
        """
        Initialize the log collector with all components.
        
        Args:
            config: CollectionConfig instance
            
        Returns:
            LogCollector instance
        """
        logger.info("Initializing log collector...")
        collector = LogCollector(config)
        logger.info("Log collector initialized successfully")
        return collector
    
    def cmd_start(self, args):
        """
        Start continuous log collection.
        
        This command starts the log collector in continuous mode, collecting
        logs at the configured interval until interrupted.
        
        Args:
            args: Parsed command-line arguments
        """
        logger.info("=== Starting Continuous Log Collection ===")
        
        # Load configuration
        self.config = self.load_configuration(args.config)
        
        # Initialize collector
        self.collector = self.initialize_collector(self.config)
        
        # Setup signal handlers for graceful shutdown
        self.setup_signal_handlers()
        
        # Start collection
        logger.info(f"Collection interval: {self.config.collection_interval_seconds}s")
        logger.info(f"Anomaly threshold: {self.config.anomaly_threshold}")
        logger.info(f"Model path: {self.config.model_path}")
        logger.info("Press Ctrl+C to stop")
        
        self.running = True
        self.collector.start()
        
        # Keep main thread alive
        try:
            while self.running:
                signal.pause()
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            if self.collector:
                self.collector.stop()
    
    def cmd_collect_once(self, args):
        """
        Perform a single collection cycle.
        
        This command collects logs once, processes them through the full pipeline,
        and then exits.
        
        Args:
            args: Parsed command-line arguments
        """
        logger.info("=== Single Collection Cycle ===")
        
        # Load configuration
        self.config = self.load_configuration(args.config)
        
        # Initialize collector
        self.collector = self.initialize_collector(self.config)
        
        # Perform single collection
        logger.info("Collecting metrics...")
        feature_vector = self.collector.collect_once()
        
        if feature_vector:
            logger.info("Collection successful:")
            logger.info(f"  CPU Usage: {feature_vector.cpu_usage:.1f}%")
            logger.info(f"  Memory Usage: {feature_vector.memory_usage:.1f}%")
            logger.info(f"  Process Count: {feature_vector.process_count}")
            logger.info(f"  Network Connections: {feature_vector.network_connections}")
            logger.info(f"  Failed Logins: {feature_vector.failed_logins}")
            logger.info(f"  Unique IPs: {feature_vector.unique_ip_count}")
            logger.info(f"  Timestamp: {feature_vector.timestamp}")
            
            # Export graph if requested
            if args.export_graph:
                output_path = args.output or "logs/attack_graph.json"
                if self.collector.export_attack_graph(output_path):
                    logger.info(f"Attack graph exported to: {output_path}")
            
            logger.info("Collection completed successfully")
            return 0
        else:
            logger.error("Collection failed")
            return 1
    
    def cmd_export_graph(self, args):
        """
        Export the current attack graph to JSON.
        
        This command loads the collector (which restores any existing graph state),
        and exports the attack graph to a JSON file.
        
        Args:
            args: Parsed command-line arguments
        """
        logger.info("=== Export Attack Graph ===")
        
        # Load configuration
        self.config = self.load_configuration(args.config)
        
        # Initialize collector (this will restore graph state if available)
        self.collector = self.initialize_collector(self.config)
        
        # Determine output path
        output_path = args.output or "logs/attack_graph.json"
        
        # Export graph
        logger.info(f"Exporting attack graph to: {output_path}")
        if self.collector.export_attack_graph(output_path):
            logger.info("Export successful")
            
            # Show highest risk path if available
            risk_path = self.collector.get_highest_risk_path()
            if risk_path:
                logger.info(f"Highest risk path: {' -> '.join(risk_path)}")
            else:
                logger.info("No high-risk paths found in graph")
            
            return 0
        else:
            logger.error("Export failed")
            return 1
    
    def run(self, argv=None):
        """
        Main entry point for the application.
        
        Parses command-line arguments and dispatches to appropriate command handler.
        
        Args:
            argv: Command-line arguments (defaults to sys.argv)
            
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        # Create argument parser
        parser = argparse.ArgumentParser(
            description='Kaisen Log Collection Backend - Security monitoring and anomaly detection',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s start                          # Start continuous collection
  %(prog)s collect-once                   # Single collection cycle
  %(prog)s collect-once --export-graph    # Collect once and export graph
  %(prog)s export-graph                   # Export current attack graph
  %(prog)s export-graph -o graph.json     # Export to custom path
            """
        )
        
        # Global arguments
        parser.add_argument(
            '-c', '--config',
            default='config.json',
            help='Path to configuration file (default: config.json)'
        )
        
        # Subcommands
        subparsers = parser.add_subparsers(
            dest='command',
            help='Command to execute',
            required=True
        )
        
        # Start command
        parser_start = subparsers.add_parser(
            'start',
            help='Start continuous log collection'
        )
        
        # Collect-once command
        parser_collect = subparsers.add_parser(
            'collect-once',
            help='Perform a single collection cycle'
        )
        parser_collect.add_argument(
            '--export-graph',
            action='store_true',
            help='Export attack graph after collection'
        )
        parser_collect.add_argument(
            '-o', '--output',
            help='Output path for graph export (default: logs/attack_graph.json)'
        )
        
        # Export-graph command
        parser_export = subparsers.add_parser(
            'export-graph',
            help='Export the current attack graph to JSON'
        )
        parser_export.add_argument(
            '-o', '--output',
            help='Output path for graph JSON (default: logs/attack_graph.json)'
        )
        
        # Parse arguments
        args = parser.parse_args(argv)
        
        # Dispatch to command handler
        try:
            if args.command == 'start':
                return self.cmd_start(args)
            elif args.command == 'collect-once':
                return self.cmd_collect_once(args)
            elif args.command == 'export-graph':
                return self.cmd_export_graph(args)
            else:
                parser.print_help()
                return 1
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            return 1


def main():
    """Entry point for the application."""
    app = LogCollectionMain()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
