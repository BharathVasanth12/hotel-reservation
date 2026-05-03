import os
import sys

from google.cloud import storage

from config.paths_config import CONFIG_FILE_PATH, RAW_DIR, RAW_FILE_PATH
from src.logger import logging
from src.custom_exception import CustomException
from utils.common_functions import read_yaml_file


class DataIngestion:
    def __init__(self, config):
        if isinstance(config, str):
            config = read_yaml_file(config)

        self.config = config['data_ingestion']
        self.bucket_name = self.config['bucket_name']
        self.bucket_file_name = self.config['bucket_file_name']

        os.makedirs(RAW_DIR, exist_ok=True)

        logging.info(
            f"DataIngestion started with {self.bucket_name} and file is {self.bucket_file_name}"
        )

    def download_csv_from_gcp(self):
        try:
            logging.info(
                f"Attempting to download {self.bucket_file_name} from GCP bucket {self.bucket_name}"
            )
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(self.bucket_file_name)
            blob.download_to_filename(RAW_FILE_PATH)
            logging.info(
                f"Successfully downloaded {self.bucket_file_name} from GCP bucket {self.bucket_name}"
            )
        except Exception as e:
            logging.error(f"Error downloading file from GCP: {str(e)}")
            raise CustomException(e, sys)

    def run(self):
        try:
            logging.info("Starting data ingestion process.")
            if os.path.isfile(RAW_FILE_PATH) and os.path.getsize(RAW_FILE_PATH) > 0:
                logging.info(
                    f"Raw dataset already present at {RAW_FILE_PATH}; skipping GCP download"
                )
            else:
                self.download_csv_from_gcp()
            logging.info(
                "Train/test split runs in model_training.py after preprocessing."
            )
            logging.info("Data ingestion process completed successfully.")
        except Exception as e:
            logging.error(f"Error in data ingestion process: {str(e)}")
            raise CustomException(e, sys)
        

if __name__ == "__main__":
    try:
        data_ingestion = DataIngestion(CONFIG_FILE_PATH)
        data_ingestion.run()
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
        raise CustomException(e, sys)