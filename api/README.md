# Spark Monitoring Dashboard Deployment Guide

## Overview
This guide explains how to deploy the Spark performance monitoring dashboard to Grafana using the API.

## Prerequisites
- Running Grafana instance (http://localhost:3000)
- Admin access to Grafana
- Spark metrics configured and flowing to Prometheus

## Steps

### 1. Create Service Account Token
1. Log into Grafana UI
2. Navigate to: Home → Administration → Service accounts
3. Click "+ Create service account"
4. Configure:
   - Display name: spark-monitor
   - Role: Admin
5. Click "Create"
6. Click "Add service account token"
7. Save the generated token securely

### 2. Deploy Dashboard
Run the following command, replacing `<YOUR-TOKEN>` with the service account token:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  -d @api/spark_monitoring_dashboard.json \
  http://localhost:3000/api/dashboards/db
```

### 3. Access Dashboard
1. Navigate to Grafana UI
2. Go to Dashboards → Browse
3. Find "Spark Cluster Performance Dashboard"

## Dashboard Features
- Real-time cluster metrics
- Memory utilization tracking
- GC performance analysis
- CPU usage monitoring
- Resource distribution visualization

## Security Notes
- Store service account tokens securely
- Use minimal required permissions for service accounts
- Rotate tokens periodically following security best practices

## Maintenance
- Update dashboard configuration as needed via API
- Monitor dashboard performance
- Keep Grafana and plugins updated