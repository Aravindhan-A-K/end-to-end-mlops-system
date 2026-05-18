from pydantic import BaseModel, create_model, Field
from typing import Literal
import mlflow 
import json
import os
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

#artifact_path = mlflow.artifact.download_artifacts(run_id = "", artifact_path = "schema.json")
#mlflow.set_tracking_uri(os.getenv("MODEL_TRACKING_URI"))
environment = os.getenv("ENVIRONMENT", "Production")
MODEL_NAME = "First model"

# local_model_path = mlflow.artifacts.download_artifacts(f"models:/{MODEL_NAME}/{environment}")
# artifact_path = os.path.join(
#     local_model_path,
#     "schema.json"
# )
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

with open(artifact_path) as f:
    schemas = json.load(f)

fields = {}

def map_dtype(dtype):
    if "int" in dtype:
        return int
    elif "float" in dtype:
        return float
    elif "str" in dtype:
        return str
    else:
        return str

for col, meta in schemas.items():
    dtype = map_dtype(meta["dtype"])

    if "allowed_values" in meta and meta["allowed_values"]:
        fields[col] = (Literal[tuple(meta["allowed_values"])], Field(...))
    elif dtype in [int, float]:
        fields[col] = (dtype, Field(..., ge=meta.get("min"), le=meta.get("max")))
    else:
        fields[col] = (dtype, Field(...))
RequestModel = create_model("RequestModel", **fields)

class ResponseModel(BaseModel):
    SalePrice: float