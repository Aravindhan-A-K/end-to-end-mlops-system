import json

import pandas as pd
from fastapi import Request
from fastapi import BackgroundTasks
from app.api.schemas import RequestModel
from app.core.logger import logger
import time
from mlflow.tracking import MlflowClient
import mlflow
import os

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



def predict_service(request:Request, data:RequestModel, background_task:BackgroundTasks, model):
    start_time = time.time()
    prediction = None
    try:
        input_dict = data.model_dump()
        input_df = pd.DataFrame([input_dict])
        for col, meta in schemas.items():
            if "allowed_values" in meta:
                input_df[col] = input_df[col].astype("category")
            elif meta["dtype"] == "float64":
                input_df[col] = input_df[col].astype(float)
            elif meta["dtype"] == "int64":
                input_df[col] = input_df[col].astype(int)
        
        input_df = input_df.reindex(columns=model.feature_names_in_)

        prediction = model.predict(input_df)
        prediction = {'SalePrice': float(prediction[0])}
        return prediction
    finally:
        latency = time.time() - start_time
        logger.info("Prediction successful" if prediction else "Prediction failed", 
                    extra={
                    'correlation_id': getattr(request.state, "correlation_id" , None),
                    'model_latency': latency,
                    'prediction_value': prediction})
