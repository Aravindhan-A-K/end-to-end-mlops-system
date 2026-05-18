import pandas as pd
import os
import boto3
import json
from io import StringIO


from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.metrics import root_mean_squared_error, accuracy_score

import mlflow

column_names = [
    "instant",
    "date",
    "season",
    "year",
    "month",
    "hour",
    "is_holiday",
    "weekday",
    "is_working_day",
    "weather_condition",
    "temperature",
    "feels_like_temperature",
    "humidity",
    "wind_speed",
    "casual_users",
    "registered_users",
    "total_rentals"
]

#df = pd.read_csv('./Data/hour.csv', names=column_names, skiprows = 1)
endpoint_url = os.getenv("S3_ENDPOINT_URL")

if endpoint_url:
    s3_client = boto3.client(
        "s3",
        endpoint_url=endpoint_url
    )
else:
    s3_client = boto3.client("s3")

response = s3_client.get_object(Bucket='mlops-artifacts-aravindh-ml', Key='Data/hour.csv')
csv_content = response["Body"].read().decode("utf-8")

# Convert to pandas dataframe
df = pd.read_csv(StringIO(csv_content), names=column_names, skiprows = 1)

df.info()
df.head()

df.set_index('instant', inplace=True)

df.info()

df.drop(columns=['casual_users', 'registered_users'], inplace=True)


df['year'] = df['year'].replace(0, 2011)
df["year"] = df["year"].replace(1, 2012)

df.dtypes

df['season'] = df['season'].astype('category')
df["year"] = df['year'].astype('category')
df["month"] = df['month'].astype('category')
df["hour"] = df['hour'].astype('category')
df['date'] = pd.to_datetime(df['date'])
df["is_holiday"] = df['is_holiday'].astype('category')
df["weekday"] = df['weekday'].astype('category')
df["is_working_day"] = df['is_working_day'].astype('category')
df["weather_condition"] = df['weather_condition'].astype('category')


#df.corr()

#Tree model

tree_df = df

tree_df = tree_df.drop(columns=['date', 'feels_like_temperature'])

X = tree_df.drop(columns=['total_rentals'])
y = tree_df['total_rentals']

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
mlflow.set_experiment("Bike_sharing_model")

x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

def generate_schema(df: pd.DataFrame):
    schema = {}
    for col in df.columns:
        dtype = df[col].dtype
        metadata = {"dtype": str(dtype), "required": True}

        if pd.api.types.is_numeric_dtype(dtype):
            metadata["min"] = df[col].min()
            metadata["max"] = df[col].max()
        else:
            unique_values = df[col].dropna().unique()
            n_unique = len(unique_values)
            
            if n_unique <= 30:
                metadata["allowed_values"] = unique_values.tolist()
        schema[col] = metadata
    return schema

schema = generate_schema(x_train)
with open("schema.json", "w") as f:
    json.dump(schema, f, indent=4)

with mlflow.start_run():

    model = XGBRegressor(
        n_estimators = 300,
        learning_rate = 0.1,
        max_depth = 6,
        subsample = 0.8,
        colsample_bytree = 0.8,
        n_jobs = -1,
        random_state=42,
        objective = 'reg:squarederror',
        enable_categorical=True,
        min_child_weight = 5, gamma = 20,
        reg_lambda = 5)#,
        #reg_alpha = 25000)

    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)

    y_train_pred = model.predict(x_train)

    mlflow.log_param("n_estimators", 300)
    mlflow.log_param("learning_rate", 0.1)
    mlflow.log_param("max_depth", 6)
    mlflow.log_param("subsample", 0.8)
    mlflow.log_param("colsample_bytree", 0.8)
    mlflow.log_param("n_jobs", -1)
    mlflow.log_param("random_state", 42)
    mlflow.log_param("objective", "reg:squarederror")
    mlflow.log_param("enable_categorical", True)
    mlflow.log_param("min_child_weight", 5)
    mlflow.log_param("gamma", 20)
    mlflow.log_param("reg_lambda", 5)

    mlflow.log_metric("rmse", root_mean_squared_error(y_test, y_pred))
    mlflow.log_artifact("schema.json", artifact_path="model")
    mlflow.sklearn.log_model(model, artifact_path="model")


