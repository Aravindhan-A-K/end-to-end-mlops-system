import mlflow 
import json
import os
from mlflow.tracking import MlflowClient

def load_schema():
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
    environment = os.getenv("ENVIRONMENT", "Production")
    MODEL_NAME = "First model"
    client = MlflowClient()

    model_versions = list(client.search_model_versions(
        f"name='{MODEL_NAME}'"
    ))

    production_model = next(
        mv for mv in model_versions
        if mv.current_stage == "Production"
    )

    run_id = production_model.run_id

    artifact_path = mlflow.artifacts.download_artifacts(
        run_id=run_id,
        artifact_path="model/schema.json"
    )
    with open(artifact_path, 'r') as f:
        schemas = json.load(f)
    return schemas

def map_dtype(dtype):
    if "int" in dtype:
        return int
    elif "float" in dtype:
        return float
    elif "str" in dtype:
        return str
    else:
        return str

def generate_valid_payload():
    schema = load_schema()
    data = {}
    for col, meta in schema.items():
        dtype = map_dtype(meta["dtype"])

        if 'allowed_values' in meta and meta['allowed_values']:
            data[col] = meta['allowed_values'][0]
        elif dtype in [int, float]:
            data[col] = int(meta['min']+meta['max'])/2
        else:
            data[col] = "Testing the ML API"
    return data

