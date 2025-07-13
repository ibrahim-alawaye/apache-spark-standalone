"""
Simple Prefect Deployment Script for Prefect 3.x
"""

import sys
import subprocess
import os

def deploy_with_prefect_cli(
    flow_file: str,
    flow_function: str,
    deployment_name: str,
    schedule: str = None,
    work_pool: str = "default"
):
    """Deploy using prefect CLI with flexible flow function."""
    
    cmd = [
        "prefect", "deploy", 
        f"{flow_file}:{flow_function}",
        "--name", deployment_name,
        "--pool", work_pool
    ]
    
    if schedule:
        cmd.extend(["--cron", schedule])
    
    print(f"🚀 Deploying: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Deployment successful!")
            print(result.stdout)
            return True
        else:
            print("❌ Deployment failed!")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False

def deploy_data_pipeline():
    """Deploy the data pipeline."""
    return deploy_with_prefect_cli(
        flow_file="pipeline_workflow.py",
        flow_function="data_pipeline_flow",
        deployment_name="data-pipeline",
        schedule="0 9 * * *"  # Daily at 9 AM
    )

def deploy_health_check():
    """Deploy health check."""
    return deploy_with_prefect_cli(
        flow_file="health_check_flow.py",
        flow_function="spark_health_flow",
        deployment_name="health-check",
        schedule="*/15 * * * *"  # Every 15 minutes
    )

def deploy_simple():
    """Deploy without schedule."""
    return deploy_with_prefect_cli(
        flow_file="pipeline_workflow.py",
        flow_function="data_pipeline_flow",
        deployment_name="data-pipeline-simple"
    )

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python deployment.py --data-pipeline")
        print("  python deployment.py --health-check") 
        print("  python deployment.py --simple")
        print("  python deployment.py <flow_file> <flow_function> <deployment_name> [schedule]")
        print("")
        print("Examples:")
        print("  python deployment.py pipeline_workflow.py data_pipeline_flow my-pipeline")
        print("  python deployment.py health_check_flow.py spark_health_flow health-check '*/15 * * * *'")
        return
    
    if sys.argv[1] == "--data-pipeline":
        deploy_data_pipeline()
    elif sys.argv[1] == "--health-check":
        deploy_health_check()
    elif sys.argv[1] == "--simple":
        deploy_simple()
    elif len(sys.argv) >= 4:
        flow_file = sys.argv[1]
        flow_function = sys.argv[2]
        deployment_name = sys.argv[3]
        schedule = sys.argv[4] if len(sys.argv) > 4 else None
        
        # Check if file exists
        if not os.path.exists(flow_file):
            print(f"❌ Error: File '{flow_file}' not found!")
            print(f"📁 Current directory: {os.getcwd()}")
            print(f"📄 Available Python files:")
            for f in os.listdir('.'):
                if f.endswith('.py'):
                    print(f"   {f}")
            return
        
        deploy_with_prefect_cli(flow_file, flow_function, deployment_name, schedule)
    else:
        print("❌ Invalid arguments")
        print("Use 'python deployment.py' for usage information")

if __name__ == "__main__":
    main()
