import os
import requests
from typing import List, Dict
import sys
from pathlib import Path

# Set root directory jar folder
JARS_DIR = "jars"
MAVEN_BASE_URL = "https://repo1.maven.org/maven2"

# Define all required JARs with their Maven coordinates
REQUIRED_JARS = {
    # Delta Lake Core
    "delta-core": {"group": "io.delta", "artifact": "delta-core_2.12", "version": "2.4.0"},
    "delta-storage": {"group": "io.delta", "artifact": "delta-storage", "version": "2.4.0"},
    
    # AWS/S3 Support
    "hadoop-aws": {"group": "org.apache.hadoop", "artifact": "hadoop-aws", "version": "3.3.4"},
    "aws-java-sdk-bundle": {"group": "com.amazonaws", "artifact": "aws-java-sdk-bundle", "version": "1.12.261"},
    
    # Parquet Support
    "parquet-hadoop": {"group": "org.apache.parquet", "artifact": "parquet-hadoop", "version": "1.12.3"},
    "parquet-column": {"group": "org.apache.parquet", "artifact": "parquet-column", "version": "1.12.3"},
    
    # JSON Support
    "jackson-databind": {"group": "com.fasterxml.jackson.core", "artifact": "jackson-databind", "version": "2.13.4"},
    
    # Scala (for Delta Lake)
    "scala-library": {"group": "org.scala-lang", "artifact": "scala-library", "version": "2.12.17"},
    
    # Database Connectors
    "postgresql": {"group": "org.postgresql", "artifact": "postgresql", "version": "42.5.1"},
    
    # Kafka Support
    "spark-sql-kafka": {"group": "org.apache.spark", "artifact": "spark-sql-kafka-0-10_2.12", "version": "3.4.1"}
}

def create_jars_directory():
    jars_path = Path(JARS_DIR)
    jars_path.mkdir(exist_ok=True)
    print(f"Created/verified directory: {jars_path.absolute()}")
    return jars_path

def download_jar(group: str, artifact: str, version: str) -> bool:
    group_path = group.replace(".", "/")
    jar_name = f"{artifact}-{version}.jar"
    url = f"{MAVEN_BASE_URL}/{group_path}/{artifact}/{version}/{jar_name}"
    output_path = os.path.join(JARS_DIR, jar_name)
    
    if os.path.exists(output_path):
        print(f"Skipping {jar_name} (already exists)")
        return True
    
    try:
        print(f"Downloading {jar_name}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"Successfully downloaded {jar_name}")
        return True
        
    except Exception as e:
        print(f"Error downloading {jar_name}: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return False

def verify_downloads():
    jars_path = Path(JARS_DIR)
    jar_files = list(jars_path.glob("*.jar"))
    total_size = sum(f.stat().st_size for f in jar_files)
    
    print(f"\nVerification Summary:")
    print(f"Total JARs: {len(jar_files)}")
    print(f"Total size: {total_size:,} bytes")
    
    for jar_file in sorted(jar_files):
        print(f"Verified: {jar_file.name}")
    
    return len(jar_files) > 0

def main():
    print("Starting JAR download process")
    create_jars_directory()
    
    success_count = 0
    for jar_name, jar_info in REQUIRED_JARS.items():
        if download_jar(jar_info["group"], jar_info["artifact"], jar_info["version"]):
            success_count += 1
    
    print(f"\nDownload Summary:")
    print(f"Successfully downloaded: {success_count}/{len(REQUIRED_JARS)} JARs")
    
    if verify_downloads():
        print("JAR download process completed successfully")
        return 0
    else:
        print("JAR download process failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
