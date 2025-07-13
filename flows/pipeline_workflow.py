from prefect import flow, task
from spark_init import copy_and_submit_python_job

@task
def run_data_pipeline():
    return copy_and_submit_python_job(
        local_python_file="data_pipeline.py",
        spark_args={"executor-memory": "1g"}
    )

@flow
def data_pipeline_flow():
    pipeline_result = run_data_pipeline()
    return pipeline_result

if __name__ == "__main__":
    result = data_pipeline_flow()
    print(f"Pipeline result: {result}")
