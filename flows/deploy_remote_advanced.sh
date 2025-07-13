#!/bin/bash

echo "🚀 Advanced Remote Prefect Deployment"
echo "====================================="

# Function to check if container exists and is running
check_container() {
    local container_name=$1
    if docker ps --format "table {{.Names}}" | grep -q "^${container_name}$"; then
        return 0
    else
        return 1
    fi
}

# Function to list available workers
list_workers() {
    echo "🔍 Available Prefect workers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}" | grep -E "(worker|prefect)" | head -10
}

# Function to show worker files
show_worker_files() {
    local worker=$1
    echo "📄 Available files in $worker:"
    docker exec "$worker" bash -c "
        cd /root/flows 2>/dev/null || cd /root || cd /
        find . -name '*.py' -type f 2>/dev/null | grep -E '(flow|workflow)' | head -10
    "
}

# Function to show pre-configured deployments
show_preconfig() {
    echo "⚡ Pre-configured deployments:"
    echo "1. --data-pipeline     (Daily at 9 AM)"
    echo "2. --health-check      (Every 15 minutes)"
    echo "3. --simple            (No schedule)"
}

# List of possible worker containers
WORKERS=(
    "spark-engine-worker-1-1"
    "spark-engine-worker-2-1" 
    "spark-engine-worker-3-1"
)

# Check command line arguments for quick deployment
if [ "$1" = "--list-workers" ]; then
    list_workers
    exit 0
fi

if [ "$1" = "--help" ]; then
    echo "Usage:"
    echo "  $0                    # Interactive mode"
    echo "  $0 --list-workers     # List available workers"
    echo "  $0 --quick <worker>   # Quick deployment on specific worker"
    echo "  $0 --help             # Show this help"
    exit 0
fi

# Find available worker
SELECTED_WORKER=""

if [ "$1" = "--quick" ] && [ -n "$2" ]; then
    if check_container "$2"; then
        SELECTED_WORKER="$2"
        echo "🎯 Using specified worker: $SELECTED_WORKER"
    else
        echo "❌ Worker '$2' not found or not running"
        list_workers
        exit 1
    fi
else
    echo "🔍 Checking for available Prefect workers..."
    
    for worker in "${WORKERS[@]}"; do
        if check_container "$worker"; then
            echo "✅ Found: $worker"
            SELECTED_WORKER="$worker"
            break
        fi
    done
    
    if [ -z "$SELECTED_WORKER" ]; then
        echo "❌ No Prefect workers found running!"
        list_workers
        exit 1
    fi
fi

echo "🎯 Using worker: $SELECTED_WORKER"
echo ""

# Show deployment options
echo "🎛️ Deployment Options:"
echo "======================"
echo "1. Pre-configured deployment"
echo "2. Custom deployment"
echo "3. Interactive shell"
echo "4. List existing deployments"

read -p "Choose option (1-4): " OPTION

case $OPTION in
    1)
        echo ""
        show_preconfig
        echo ""
        read -p "Enter pre-config option (--data-pipeline, --health-check, --simple): " PRECONFIG
        
        DEPLOY_CMD="python deployment.py $PRECONFIG"
        
        echo ""
        echo "🚀 Running pre-configured deployment..."
        docker exec -it "$SELECTED_WORKER" bash -c "
            cd /root/flows && 
            echo '🚀 Executing: $DEPLOY_CMD' &&
            $DEPLOY_CMD
        "
        ;;
        
    2)
        echo ""
        show_worker_files "$SELECTED_WORKER"
        echo ""
        
        read -p "Enter flow file (e.g., pipeline_workflow.py): " FLOW_FILE
        read -p "Enter flow function (e.g., data_pipeline_flow): " FLOW_FUNCTION  
        read -p "Enter deployment name (e.g., my-deployment): " DEPLOYMENT_NAME
        read -p "Enter schedule (optional, e.g., '0 9 * * *'): " SCHEDULE
        
        # Validate inputs
        if [ -z "$FLOW_FILE" ] || [ -z "$FLOW_FUNCTION" ] || [ -z "$DEPLOYMENT_NAME" ]; then
            echo "❌ Error: Flow file, function, and deployment name are required!"
            exit 1
        fi
        
        # Build the deployment command
        if [ -z "$SCHEDULE" ]; then
            DEPLOY_CMD="python deployment.py $FLOW_FILE $FLOW_FUNCTION $DEPLOYMENT_NAME"
        else
            DEPLOY_CMD="python deployment.py $FLOW_FILE $FLOW_FUNCTION $DEPLOYMENT_NAME '$SCHEDULE'"
        fi
        
        echo ""
        echo "📋 Deployment Summary:"
        echo "======================"
        echo "Worker: $SELECTED_WORKER"
        echo "Flow File: $FLOW_FILE"
        echo "Flow Function: $FLOW_FUNCTION"
        echo "Deployment Name: $DEPLOYMENT_NAME"
        echo "Schedule: ${SCHEDULE:-'None'}"
        echo ""
        
        read -p "Proceed with deployment? (y/N): " CONFIRM
        
        if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
            echo "❌ Deployment cancelled"
            exit 0
        fi
        
        echo ""
        echo "🚀 Executing deployment..."
        docker exec -it "$SELECTED_WORKER" bash -c "
            cd /root/flows && 
            echo '🚀 Executing: $DEPLOY_CMD' &&
            $DEPLOY_CMD
        "
        ;;
        
    3)
        echo ""
        echo "🐚 Opening interactive shell in $SELECTED_WORKER..."
        echo "💡 Tip: cd /root/flows && python deployment.py --help"
        docker exec -it "$SELECTED_WORKER" bash
        ;;
        
    4)
        echo ""
        echo "📋 Listing existing deployments..."
        docker exec "$SELECTED_WORKER" bash -c "
            echo '📋 Current deployments:' &&
            prefect deployment ls
        "
        ;;
        
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "✅ Operation completed!"
echo ""
echo "🛠️ Useful commands:"
echo "List deployments: docker exec $SELECTED_WORKER prefect deployment ls"
echo "Run deployment: docker exec $SELECTED_WORKER prefect deployment run <name>"
echo "Worker logs: docker logs $SELECTED_WORKER"
echo "Worker shell: docker exec -it $SELECTED_WORKER bash"
