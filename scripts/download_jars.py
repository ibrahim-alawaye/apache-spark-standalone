import os
import requests
from typing import List, Dict

JARS_DIR = "jars"
MAVEN_BASE_URL = "https://repo1.maven.org/maven2"

MINIO_JARS = {
    "hadoop-aws": {
        "group": "org.apache.hadoop",
        "artifact": "hadoop-aws",
        "version": "3.3.4"
    },
    "aws-java-sdk-bundle": {
        "group": "com.amazonaws",
        "artifact": "aws-java-sdk-bundle",
        "version": "1.12.261"
    }
}

def download_jar(group: str, artifact: str, version: str) -> None:
    group_path = group.replace(".", "/")
    jar_name = f"{artifact}-{version}.jar"
    url = f"{MAVEN_BASE_URL}/{group_path}/{artifact}/{version}/{jar_name}"
    
    os.makedirs(JARS_DIR, exist_ok=True)
    output_path = os.path.join(JARS_DIR, jar_name)
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Downloaded {jar_name}")

def main():
    for jar_info in MINIO_JARS.values():
        download_jar(
            jar_info["group"],
            jar_info["artifact"],
            jar_info["version"]
        )

if __name__ == "__main__":
    main()