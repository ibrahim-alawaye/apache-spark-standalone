from test_spark_integration import test_spark_integration_flow

test_spark_integration_flow.deploy(
    name="spark-integration-test",
    work_pool_name="default",
    push=False  
)
