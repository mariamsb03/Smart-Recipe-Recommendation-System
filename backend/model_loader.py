import os
import mlflow
import mlflow.pyfunc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

_model = None
_expected_features = None


def load_production_model():
    global _model, _expected_features

    if _model is not None:
        return _model

    # ---- ENV ----
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME")
    model_name = os.getenv("MLFLOW_MODEL_NAME")
    model_version = os.getenv("MLFLOW_MODEL_VERSION")

    mlflow_username = os.getenv("MLFLOW_TRACKING_USERNAME")
    mlflow_password = os.getenv("MLFLOW_TRACKING_PASSWORD")

    if not all([tracking_uri, experiment_name, model_name, model_version]):
        raise RuntimeError(
            "Missing one of: MLFLOW_TRACKING_URI, "
            "MLFLOW_EXPERIMENT_NAME, "
            "MLFLOW_MODEL_NAME, "
            "MLFLOW_MODEL_VERSION"
        )

    # ---- AUTH ----
    if mlflow_username and mlflow_password:
        os.environ["MLFLOW_TRACKING_USERNAME"] = mlflow_username
        os.environ["MLFLOW_TRACKING_PASSWORD"] = mlflow_password

    # ---- MLFLOW CONFIG ----
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)

    model_uri = f"models:/{model_name}/{model_version}"

    print(f"🔒 Loading MLflow model: {model_uri}")
    print(f"🧪 MLflow experiment: {experiment_name}")

    # ---- LOAD MODEL ----
    _model = mlflow.pyfunc.load_model(model_uri)

    print("✅ ML model loaded successfully")
    return _model


def get_expected_features():
    return _expected_features
