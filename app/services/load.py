import mlflow
import os


model = None

def set_model():
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
    environment = os.getenv("ENVIRONMENT", "Production")
    global model 
    MODEL_NAME = "First model"

    model = mlflow.sklearn.load_model(f"models:/{MODEL_NAME}/{environment}")

def get_model():
    return model