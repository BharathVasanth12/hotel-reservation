import os

################# Data Ingestion Configurations #################

RAW_DIR = "artifacts/raw"

RAW_FILE_PATH = os.path.join(RAW_DIR, "hotel_reservations.csv")

TRAIN_FILE_PATH = os.path.join(RAW_DIR, "train_data", "train.csv")

TEST_FILE_PATH = os.path.join(RAW_DIR, "test_data", "test.csv")

CONFIG_FILE_PATH = os.path.join("config", "config.yaml")

################## Data Preprocessing Configurations ##################

PROCESSED_DIR = "artifacts/processed"

PROCESSED_TRAIN_FILE_PATH = os.path.join(PROCESSED_DIR, "train_data", "train_processed.csv")

PROCESSED_TEST_FILE_PATH = os.path.join(PROCESSED_DIR, "test_data", "test_processed.csv")

################## Model Training ##################

MODEL_OUTPUT_PATH = os.path.join("artifacts", "model", "hotel_reservation_model.joblib")
