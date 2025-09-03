# Kubeflow Pipeline - Model Registry Integration

This project contains a [hello-world](https://www.kubeflow.org/docs/components/pipelines/getting-started/) Kubeflow Pipeline that _additionally_ demonstrates how to integrate with a Model Registry for ML model versioning and tracking. The pipeline showcases authentication using Kubernetes service account tokens (Model Registry in OCP) and model registration with comprehensive metadata.

## Pipeline Overview

The pipeline consists of a single component that:
1. Greets a recipient with a personalized message (the [classic hello-world from the KF Pipelines tutorial](https://www.kubeflow.org/docs/components/pipelines/getting-started/))
2. Authenticates with a Model Registry using Kubernetes service account token (required)
3. Registers an ML model with detailed metadata and provenance information

## Pipeline Flow

### 1. Pipeline Definition (`hello_pipeline`)
- **Input**: `recipient` (string) - The name of the person to greet (mandatory, per KF Pipelines hello-world tutorial)
- **Output**: Greeting message (string)
- **Component**: `say_hello` - The main processing component

### 2. Component Execution (`say_hello`)

The `say_hello` Kubeflow Pipelines component performs the following steps:

#### Step 1: Greeting Generation
no comment :)

#### Step 2: Service Account Token Authentication
```python
with open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r") as f:
    user_token = f.read().strip()
```
- Reads the Kubernetes service account token from the standard location
- This token is used for authenticating with the Model Registry

#### Step 3: Model Registry Connection
```python
registry = ModelRegistry(
    server_address="https://my-registry-rest.apps.rosa.mmortari-rosa2.otuf.p3.openshiftapps.com",
    author="pipeline-author",
    user_token=user_token
)
```
- Establishes connection to the Model Registry server
- Uses the service account token for authentication
- Sets the author as "pipeline-author"

#### Step 4: Model Registration
The component registers a model with the following details:
- **Model Name**: `my-model`
- **Model Version**: `v1-{run_id}` (dynamically generated using pipeline run ID)
- **Model URI**: `https://acme.org/somewhere/model.safetensors` this is typically coming from `model: Input[Model]` input parameter to this component, so `model.uri` would be used instead; harcoded for this example
- **Model Format**: vLLM version 1
- **Storage Key**: `odh-connection-resource-name`
- **Description**: "this is my model version description"

#### Step 5: Model Source Tracking
The registration includes comprehensive source tracking:
- **Source Class**: `pipelinerun` fixed string
- **Source Group**: `ds-prj1` (Data Science Project, K8s namespace) you MUST change this if running in another namespace
- **Source ID**: Pipeline run ID
- **Source Kind**: `kfp` (Kubeflow Pipelines) fixed string
- **Source Name**: Pipeline run name

#### Step 6: Metadata Storage
Custom metadata is stored with the model:
```python
metadata={
    "int_key": 1,
    "bool_key": False,
    "float_key": 3.14,
    "str_key": "str_value",
}
```

## Pipeline Execution

### Prerequisites
- Kubeflow Pipelines environment on OpenShift AI
- Access to the Model Registry server
- Proper Kubernetes service account with token access
- Required Python packages: `kfp`, `model-registry`

### Running the Pipeline
1. Compile the pipeline:
   ```bash
   uv run helloworld.py
   ```

2. Upload the generated `helloworld.yaml` to your Kubeflow Pipelines environment

> ![NOTE]
> The file `helloworld.yaml` is under source control so you can directly upload this to the Pipeline server from this repo.

3. Execute the pipeline with a recipient name parameter

### Input Parameters
- `recipient`: The name of the person to greet (required) per hello-world tutorial

### Output
- Returns the greeting message as a string

## Screenshots

Notice the `Registered from`:

![](/Screenshot%202025-09-03%20at%2021.33.38%20(2).png)

Folling the hyperlink leads to the originating PipelineRun (as expected):

![](/Screenshot%202025-09-03%20at%2021.33.53%20(2).png)

## Additional Screenshots

You must setup that SAs in the `ds-prj1` Data Science Project K8s Namespace have access to the Model Registry:

![](/Screenshot%202025-09-03%20at%2021.42.46%20(2).png)
