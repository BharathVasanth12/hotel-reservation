import os

################# Data Ingestion Configurations #################

RAW_DIR = "artifacts/raw"

RAW_FILE_PATH = os.path.join(RAW_DIR, "hotel_reservations.csv")

CONFIG_FILE_PATH = os.path.join("config", "config.yaml")

################## Data Preprocessing Configurations ##################

PROCESSED_DIR = "artifacts/processed"

################## Model Training ##################

MODEL_OUTPUT_PATH = os.path.join("artifacts", "model", "hotel_reservation_model.joblib")
