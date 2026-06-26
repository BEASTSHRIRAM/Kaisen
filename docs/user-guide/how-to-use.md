# How to Use Kaisen

This guide will walk you through using Kaisen effectively for security monitoring and incident response.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Working with Alerts](#working-with-alerts)
4. [Attack Graph Analysis](#attack-graph-analysis)
5. [Monitoring Suspicious IPs](#monitoring-suspicious-ips)
6. [Viewing System Logs](#viewing-system-logs)
7. [Best Practices](#best-practices)

## Getting Started

### Accessing the Dashboard

Once Kaisen is running, you can access the dashboard through:

1. **Electron App**: The desktop application opens automatically when you run `npm run electron:dev`
2. **Web Browser**: Navigate to [http://localhost:5173](http://localhost:5173)

### First Time Setup

When you first open Kaisen:

1. The dashboard will display "Loading..." while connecting to the backend
2. Within 7 seconds, you'll see the first metrics appear
3. The system automatically starts monitoring your infrastructure

## Dashboard Overview

The main dashboard provides a comprehensive view of your system's security status.

### Real-Time Metrics

The dashboard displays six key metrics that update every 7 seconds:

| Metric | Description | Normal Range |
|--------|-------------|--------------|
| **CPU Usage** | Processor utilization percentage | 0-80% |
| **Memory Usage** | RAM utilization percentage | 0-85% |
| **Process Count** | Number of running processes | Varies by system |
| **Network Connections** | Active network connections | Varies by workload |
| **Unique IPs** | Distinct IP addresses detected | Varies by traffic |
| **Failed Logins** | Failed authentication attempts | 0-5 per interval |

### Metric Cards

Each metric is displayed in a card showing:
- Current value with visual gauge
- Mini trend graph (last 10 data points)
- Status indicator (normal, warning, critical)

### Navigation Sidebar

Use the left sidebar to navigate between sections:

- **Dashboard**: Main overview page
- **Alerts**: Security alerts and notifications
- **Attack Graph**: Visual attack path analysis
- **Suspicious IPs**: IP reputation and risk scoring
- **Logs**: Historical system logs

## Working with Alerts

The Alerts page displays security anomalies detected by the AI system.

### Understanding Alert Severity

Alerts are categorized by severity:

| Severity | Color | Description | Action Required |
|----------|-------|-------------|-----------------|
| **Critical** | Red | Immediate threat detected | Immediate action |
| **High** | Orange | Significant anomaly | Review within 1 hour |
| **Medium** | Yellow | Unusual activity | Review within 24 hours |
| **Low** | Blue | Minor deviation | Routine review |

### Alert Details

Each alert shows:
- **Timestamp**: When the anomaly was detected
- **Severity**: Risk level
- **Source**: Affected system/component
- **Description**: What was detected
- **AI Explanation**: SHAP-based reasoning for the alert

### Filtering Alerts

Use the filter controls to:
- Filter by severity (Critical, High, Medium, Low)
- Filter by date range
- Filter by source system
- Search by keyword

### Acknowledging Alerts

To manage alert workflow:

1. Click on an alert to view details
2. Review the AI explanation and metrics
3. Click **Acknowledge** to mark as reviewed
4. Add notes about actions taken
5. Click **Resolve** when the issue is fixed

## Attack Graph Analysis

The Attack Graph page visualizes potential attack paths in your infrastructure.

### Understanding the Graph

The attack graph shows:

- **Nodes**: Represent systems, services, or vulnerabilities
  - 🟢 Green: Low risk
  - 🟡 Yellow: Medium risk
  - 🔴 Red: High risk
  - ⚫ Black: Compromised
  
- **Edges**: Represent connections or attack paths
  - Solid line: Direct connection
  - Dashed line: Indirect/potential path
  - Arrow direction: Attack flow

### Interacting with the Graph

- **Zoom**: Mouse wheel or pinch gesture
- **Pan**: Click and drag
- **Select Node**: Click to view details
- **Reset View**: Double-click background

### Node Details Panel

When you select a node, the side panel shows:
- **Node ID**: Unique identifier
- **Type**: System, service, vulnerability
- **Risk Score**: 0-100 calculated risk
- **Connected Nodes**: Direct connections
- **Attack Paths**: Paths from/to this node
- **Recommended Actions**: Mitigation suggestions

### Exporting the Graph

You can export the attack graph in multiple formats:
- **PNG**: Image for reports
- **JSON**: Data for further analysis
- **CSV**: Node/edge list for spreadsheets

Click the **Export** button in the top-right corner.

## Monitoring Suspicious IPs

The Suspicious IPs page tracks and analyzes IP addresses with suspicious activity.

### IP Risk Scoring

Each IP address receives a risk score (0-100) based on:

| Factor | Weight | Description |
|--------|--------|-------------|
| Failed Login Attempts | 30% | Repeated authentication failures |
| Connection Frequency | 25% | Abnormal connection patterns |
| Geographic Anomaly | 20% | Unexpected location |
| Known Threat Intel | 15% | Presence in threat databases |
| Behavioral Patterns | 10% | Unusual traffic patterns |

### IP Categories

IPs are categorized by risk level:

- **Critical (80-100)**: Known malicious actors, block immediately
- **High (60-79)**: Suspicious activity detected, monitor closely
- **Medium (40-59)**: Unusual patterns, routine review
- **Low (20-39)**: Minor anomalies, low priority
- **Safe (0-19)**: Normal behavior, no action needed

### IP Details

Click on any IP to view:
- **Geolocation**: Country, city, coordinates
- **ISP Information**: Organization, ASN
- **Activity Timeline**: When first seen, last seen, total events
- **Related Alerts**: All alerts associated with this IP
- **Connections**: Other IPs and systems this IP communicated with

### Actions

Available actions for each IP:
- **Whitelist**: Mark as trusted, exclude from monitoring
- **Blacklist**: Block all traffic from this IP
- **Investigate**: Create a case for deeper analysis
- **Export Data**: Download activity logs for this IP

## Viewing System Logs

The Logs page provides access to historical system data and metrics.

### Log Types

Kaisen stores several types of logs:

| Log Type | Description | Retention |
|----------|-------------|-----------|
| **System Metrics** | CPU, memory, process data | 30 days |
| **Network Logs** | Connection data, IP tracking | 30 days |
| **Security Events** | Failed logins, anomalies | 90 days |
| **Alert History** | All generated alerts | 1 year |
| **Audit Logs** | User actions, configuration changes | 1 year |

### Log Viewer Interface

The log viewer provides:
- **Real-time Updates**: New logs appear automatically
- **Filtering**: Filter by time range, log level, source, message content
- **Search**: Full-text search across all log fields
- **Export**: Download logs in JSON, CSV, or plain text formats
- **Pagination**: Navigate through large log files

### Searching Logs

Use the search bar to find specific events:

- **Exact Match**: "failed login"
- **Wildcard**: "fail*" (matches fail, failed, failure)
- **Range**: "cpu > 80" (logs where CPU > 80%)
- **Boolean**: "failed AND login" or "error OR warning"
- **Regex**: Use `/pattern/` for regular expressions

### Log Analysis

Built-in analysis tools:
- **Trend Charts**: Visualize metrics over time
- **Top Talkers**: Identify most active IPs, processes
- **Anomaly Detection**: Highlight unusual patterns
- **Correlation**: Link related events across different log types

## Best Practices

### Daily Operations

1. **Check Dashboard**: Review all metrics for anomalies (5 minutes)
2. **Review Alerts**: Address critical and high severity alerts first
3. **Monitor Attack Graph**: Check for new attack paths (weekly)
4. **Review Suspicious IPs**: Take action on high-risk IPs
5. **Check Logs**: Search for any errors or unusual activity

### Weekly Tasks

1. **Full System Review**: Export and review all alerts from the week
2. **Tune Thresholds**: Adjust anomaly detection thresholds based on false positives
3. **Update Blacklists**: Add new malicious IPs to the blacklist
4. **Review Access**: Audit user access and permissions
5. **Backup Configuration**: Export settings and backup logs

### Monthly Tasks

1. **Performance Review**: Analyze system performance and resource usage
2. **Update Signatures**: Refresh threat intelligence feeds
3. **Training Review**: Review and retrain ML models if needed
4. **Compliance Check**: Verify compliance with security policies
5. **Disaster Recovery Test**: Test backup and recovery procedures

### Security Best Practices

1. **Change Default Passwords**: Immediately change all default credentials
2. **Enable MFA**: Use multi-factor authentication for all accounts
3. **Principle of Least Privilege**: Grant minimal necessary permissions
4. **Regular Updates**: Keep all components updated with security patches
5. **Network Segmentation**: Isolate Kaisen components appropriately
6. **Encryption**: Use TLS for all communications
7. **Audit Logging**: Enable comprehensive audit logging
8. **Incident Response**: Have a plan for security incidents

### Troubleshooting Tips

1. **Check Logs First**: Always start by checking logs for errors
2. **Verify Connectivity**: Ensure all components can communicate
3. **Resource Check**: Monitor CPU, memory, and disk usage
4. **Configuration Review**: Double-check configuration files
5. **Test Incrementally**: Test changes one at a time

---

For more detailed information, refer to the specific sections in this documentation or check the [troubleshooting guide](../troubleshooting.md).