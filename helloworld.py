from kfp import dsl
from kfp import compiler

@dsl.component(base_image="registry.redhat.io/ubi9/python-311", packages_to_install=["model-registry"])
def say_hello(name: str, run_id: str = None, run_name: str = None) -> str:
    hello_text = f'Hello, {name}!'
    print(hello_text)

    import os
    try:
        with open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r") as f:
            user_token = f.read().strip()
        print("Token loaded successfully")
    except FileNotFoundError:
        raise ValueError("Service account token file not found")
    except Exception as e:
        raise ValueError("Couldn't read the token", e)
    
    from model_registry import ModelRegistry
    registry = ModelRegistry(
        server_address="https://my-registry-rest.apps.rosa.mmortari-rosa2.otuf.p3.openshiftapps.com",
        author="pipeline-author",
        user_token=user_token
    )
    print("Connected to ModelRegistry")

    print("assuming the ML model is already stored at URI")
    # typically there is an model: Input[Model] input parameter to this component, so model.uri would be used:
    some_uri = "https://acme.org/somewhere/model.safetensors"
    model_name = "my-model"
    model_version = "v1-"+run_id
    registry.register_model(
        name=model_name,
        uri=some_uri,
        version=model_version,
        description="this is my model version description",
        model_format_name="vLLM",
        model_format_version="1",
        storage_key="odh-connection-resource-name",
        model_source_class="pipelinerun",
        model_source_group="ds-prj1", # here is Data Science Project, K8s namespace
        model_source_id=run_id,
        model_source_kind="kfp",
        model_source_name=run_name,
        metadata={
            # can be one of the following types
            "int_key": 1,
            "bool_key": False,
            "float_key": 3.14,
            "str_key": "str_value",
        }
    )
    return hello_text

@dsl.pipeline
def hello_pipeline(recipient: str) -> str:
    hello_task = say_hello(name=recipient, run_id=dsl.PIPELINE_JOB_ID_PLACEHOLDER, run_name=dsl.PIPELINE_JOB_NAME_PLACEHOLDER)
    return hello_task.output


if __name__ == '__main__':
    compiler.Compiler().compile(hello_pipeline, f"{__file__[0:-3]}.yaml")
    