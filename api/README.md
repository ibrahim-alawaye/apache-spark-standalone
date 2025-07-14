# Spark Monitoring Dashboard Deployment Guide

## Overview
This guide explains how to deploy the Spark performance monitoring dashboard to Grafana using the API, configure Prometheus data sources, and verify connectivity between all monitoring components.

## Prerequisites
- Running Grafana instance (http://localhost:3000)
- Running Prometheus instance (http://localhost:9090)
- Admin access to Grafana
- Spark cluster with metrics configured and flowing to Prometheus
- Docker containers running on the same network

## Architecture Overview

The monitoring stack consists of:
- **Spark Master**: Exposes metrics on port 8080 at `/metrics/prometheus`
- **Spark Workers**: Expose metrics on port 8081 at `/metrics/prometheus`
- **Spark Applications**: Expose metrics on port 4040 at `/metrics/prometheus`
- **Prometheus**: Scrapes metrics from Spark components on port 9090
- **Grafana**: Visualizes metrics from Prometheus on port 3000

## Network Configuration

### Container Communication
When containers communicate with each other, use container names or IP addresses instead of `localhost`:

- ✅ **Correct**: `http://prometheus:9090`
- ✅ **Correct**: `http://172.20.0.X:9090` (container IP)
- ❌ **Incorrect**: `http://localhost:9090`

### Find Container Network Information

**Check container networks:**
```bash
sudo docker network ls
sudo docker inspect prometheus | grep NetworkMode
sudo docker inspect grafana | grep NetworkMode
```
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d @api/spark_monitoring_dashboard.json \
  http://localhost:3000/api/dashboards/db
  ```
**Get container IP addresses:**
```bash
sudo docker inspect prometheus | grep '"IPAddress"'
sudo docker inspect grafana | grep '"IPAddress"'
```

**Connect containers to same network if needed:**
```bash
sudo docker network connect spark-engine_spark-network grafana
```

## Step 1: Verify Prometheus Configuration

### Check Prometheus Configuration
```bash
sudo docker exec prometheus cat /etc/prometheus/prometheus.yml
```

**Expected configuration:**
```yaml
scrape_configs:
  - job_name: 'spark-master'
    static_configs:
      - targets: ['172.20.0.2:8080']
    metrics_path: /metrics/prometheus
    scrape_interval: 5s
    
  - job_name: 'spark-worker'
    static_configs:
      - targets: ['172.20.0.3:8081', '172.20.0.10:8081', '172.20.0.11:8081']
    metrics_path: /metrics/prometheus
    scrape_interval: 5s
    
  - job_name: 'spark-applications'
    static_configs:
      - targets: ['172.20.0.2:4040']
    metrics_path: /metrics/prometheus
    scrape_interval: 5s
```

### Verify Spark Metrics Endpoints

**Test Spark Master metrics:**
```bash
curl http://localhost:8080/metrics/prometheus
```

**Test Spark Worker metrics:**
```bash
curl http://localhost:32768/metrics/prometheus  # Worker 1
curl http://localhost:9092/metrics/prometheus   # Worker 1 JMX
```

**Test from within Prometheus container:**
```bash
sudo docker exec prometheus curl -s http://172.20.0.2:8080/metrics/prometheus | head -10
```

### Check Prometheus Targets Status

**Via API:**
```bash
curl -s http://localhost:9090/api/v1/targets | python3 -m json.tool
```

**Via Web UI:**
- Navigate to: http://localhost:9090/targets
- Verify all targets show as "UP"

## Step 2: Configure Grafana Data Source

### Method 1: Using Grafana Web UI

1. **Access Grafana:**
   - URL: http://localhost:3000
   - Default credentials: admin/admin

2. **Add Prometheus Data Source:**
   - Go to: Configuration → Data Sources → Add data source
   - Select: Prometheus
   - **URL**: `http://prometheus:9090` (use container name)
   - **Alternative URL**: `http://172.20.0.X:9090` (use container IP)
   - Click "Save & Test"

3. **Verify Connection:**
   - Should see: "Data source is working"

### Method 2: Using API with Service Account

**Create Service Account Token:**
1. Navigate to: Home → Administration → Service accounts
2. Click "+ Create service account"
3. Configure:
   - Display name: spark-monitor
   - Role: Admin
4. Click "Create"
5. Click "Add service account token"
6. Save the generated token securely

**Add Data Source via API:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://prometheus:9090",
    "access": "proxy",
    "isDefault": true
  }' \
  http://localhost:3000/api/datasources
```

### Troubleshooting Data Source Connection

**Test connection from Grafana container:**
```bash
sudo docker exec grafana curl -I http://prometheus:9090
```

**If connection fails, try container IP:**
```bash
# Get Prometheus IP
PROMETHEUS_IP=$(sudo docker inspect prometheus | grep '"IPAddress"' | head -1 | cut -d'"' -f4)
echo "Prometheus IP: $PROMETHEUS_IP"

# Test connection
sudo docker exec grafana curl -I http://$PROMETHEUS_IP:9090
```

## Step 3: Test Prometheus Connectivity to Spark

### Basic Connectivity Tests

**Check if Prometheus can reach Spark Master:**
```bash
sudo docker exec prometheus curl -s http://172.20.0.2:8080/metrics/prometheus | head -5
```

**Check if Prometheus can reach Spark Workers:**
```bash
sudo docker exec prometheus curl -s http://172.20.0.3:8081/metrics/prometheus | head -5
sudo docker exec prometheus curl -s http://172.20.0.10:8081/metrics/prometheus | head -5
sudo docker exec prometheus curl -s http://172.20.0.11:8081/metrics/prometheus | head -5
```

### Prometheus Query Tests

**Test these queries in Prometheus UI (http://localhost:9090):**

**1. Basic Connectivity:**
```promql
up
```

**2. Spark Master Status:**
```promql
up{job="spark-master"}
```

**3. Spark Workers Status:**
```promql
up{job="spark-worker"}
```

**4. Available Spark Metrics:**
```promql
{__name__=~"metrics_.*"}
```

**5. JVM Memory Usage:**
```promql
metrics_jvm_heap_used_Value
```

**6. JVM Memory Usage Percentage:**
```promql
(metrics_jvm_heap_used_Value / metrics_jvm_heap_max_Value) * 100
```

**7. Garbage Collection Metrics:**
```promql
metrics_jvm_G1_Young_Generation_count_Value
```

**8. Total Memory Across Cluster:**
```promql
sum(metrics_jvm_heap_used_Value)
```

### Advanced Monitoring Queries

**Memory Usage by Component:**
```promql
metrics_jvm_heap_used_Value{job=~"spark-.*"}
```

**GC Time Rate:**
```promql
rate(metrics_jvm_G1_Young_Generation_time_Value[5m])
```

**Worker Count:**
```promql
count(up{job="spark-worker"} == 1)
```

**High Memory Usage Alert:**
```promql
(metrics_jvm_heap_used_Value / metrics_jvm_heap_max_Value) * 100 > 80
```

## Step 4: Deploy Spark Dashboard

### Deploy Dashboard via API
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  -d @api/spark_monitoring_dashboard.json \
  http://localhost:3000/api/dashboards/db
```

### Verify Dashboard Deployment
1. Navigate to Grafana UI: http://localhost:3000
2. Go to: Dashboards → Browse
3. Find: "Spark Cluster Performance Dashboard"

## Dashboard Features

The deployed dashboard includes:
- **Real-time cluster metrics**: Live monitoring of Spark cluster status
- **Memory utilization tracking**: JVM heap usage across all components
- **GC performance analysis**: Garbage collection metrics and trends
- **CPU usage monitoring**: System resource utilization
- **Resource distribution visualization**: Memory and CPU allocation across workers
- **Alert panels**: Visual indicators for system health issues

## Troubleshooting

### Common Issues

**1. Connection Refused Error:**
```
Post "http://localhost:9090/api/v1/query": dial tcp [::1]:9090: connect: connection refused
```
**Solution:** Use container name `http://prometheus:9090` instead of `localhost`

**2. Targets Down in Prometheus:**
- Check if Spark containers are running: `sudo docker ps`
- Verify network connectivity: `sudo docker exec prometheus ping 172.20.0.2`
- Check Spark metrics endpoints: `curl http://localhost:8080/metrics/prometheus`

**3. No Data in Grafana:**
- Verify data source configuration uses correct URL
- Test Prometheus queries manually
- Check time range in Grafana dashboard

**4. Metrics Not Available:**
- Verify Spark metrics.properties configuration
- Restart Spark containers: `sudo docker restart spark-master`
- Check Spark logs: `sudo docker logs spark-master`

### Log Analysis

**Check Prometheus logs:**
```bash
sudo docker logs prometheus --tail 20
```

**Check Grafana logs:**
```bash
sudo docker logs grafana --tail 20
```

**Check Spark Master logs:**
```bash
sudo docker logs spark-master --tail 20
```

### Network Debugging

**Test container connectivity:**
```bash
sudo docker exec grafana ping prometheus
sudo docker exec prometheus ping 172.20.0.2
```

**Check port accessibility:**
```bash
sudo docker exec grafana telnet prometheus 9090
sudo docker exec prometheus telnet 172.20.0.2 8080
```

## Security Notes

- Store service account tokens securely
- Use minimal required permissions for service accounts
- Rotate tokens periodically following security best practices
- Consider using environment variables for sensitive configuration
- Implement network policies to restrict container communication

## Maintenance

- **Update dashboard configuration** as needed via API
- **Monitor dashboard performance** and optimize queries
- **Keep Grafana and Prometheus updated** to latest stable versions
- **Regular backup** of Grafana dashboards and Prometheus data
- **Monitor disk usage** for Prometheus time-series data
- **Review and update** alerting rules based on operational experience

## Performance Optimization

- **Use recording rules** for frequently queried metrics
- **Adjust scrape intervals** based on monitoring requirements
- **Configure retention policies** for Prometheus data
- **Optimize dashboard queries** to reduce load
- **Use appropriate time ranges** for historical analysis

## Support

For issues or questions:
- Check container logs first
- Verify network connectivity between containers
- Test individual components before troubleshooting the full stack
- Consult Prometheus and Grafana documentation for advanced configuration

---

**Quick Start Checklist:**
- [ ] Verify all containers are running
- [ ] Check Prometheus targets are UP
- [ ] Configure Grafana data source with container name
- [ ] Test basic Prometheus queries
- [ ] Deploy Spark dashboard
- [ ] Run health check script
- [ ] Verify dashboard displays data
