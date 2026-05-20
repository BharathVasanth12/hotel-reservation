from src.logger import logging
from src.custom_exception import CustomException
from config.paths_config import CONFIG_FILE_PATH, PROCESSED_DIR, RAW_FILE_PATH
from utils.common_functions import read_yaml_file, load_data
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, PowerTransformer

import pandas as pd
import numpy as np
import os
import sys

class DataPreprocessor:
    def __init__(self, raw_data_path, processed_file_path, config_path):
        self.raw_data_path = raw_data_path
        self.processed_file_path = processed_file_path
        self.config = read_yaml_file(config_path)

        processed_dir = os.path.dirname(processed_file_path)
        if not os.path.exists(processed_dir):
            os.makedirs(processed_dir, exist_ok=True)

    def preprocess_data(self, df):
        try:
            logging.info("Initiating data preprocessing")

            # Step1 : Drop the unwanted ID column
            logging.info("Initiating removal of the unwanted ID column")
            df = df.drop(columns=['Booking_ID'], axis=1)

            # Step 2: Handle duplicated rows
            logging.info("Initiating duplicated rows handling")
            if df.duplicated().sum():
                logging.info(f"Found {df.duplicated().sum()} duplicated rows. Dropping them.")
                df = df.drop_duplicates()
                logging.info(f"Dropped {df.duplicated().sum()} duplicated rows")
            else:
                logging.info("No duplicated rows found.")

            # Step 3: Handle missing values
            logging.info("Initiating missing values handling")
            if df.isnull().sum().sum():
                logging.info(f"Found {df.isnull().sum().sum()} missing values. Handling them.")
                df = df.fillna(df.median())
                logging.info(f"Handled missing values")

                # fill categorical missing values with mode
                cat_cols = df.select_dtypes(include='object').columns
                for col in cat_cols:
                    df[col] = df[col].fillna(df[col].mode()[0])
                
                # Fill numeric column nan with median if outlier exist, if not fill with mean
                num_cols = df.select_dtypes(include='number').columns
                for col in num_cols:
                    series = df[col].dropna()
                    Q1 = series.quantile(0.25)
                    Q3 = series.quantile(0.75)
                    IQR = Q3 - Q1

                    if IQR == 0:
                        has_outlier = False
                    else:
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        has_outlier = ((series < lower_bound) | (series > upper_bound)).any()

                    if has_outlier:
                        logging.info(f"Column {col} has outliers. Filling missing values with median.")
                        df[col] = df[col].fillna(df[col].median())
                    else:
                        logging.info(f"Column {col} has no outliers. Filling missing values with mean.")
                        df[col] = df[col].fillna(df[col].mean())
            else:
                logging.info("No missing values found.")
            
            # Step 4: Handle skewness
            logging.info("Initiating skewness handling")
            skewed_cols = self.config.get('data_preprocessing', {}).get('skewed_features', [])
            for col in skewed_cols:
                if col in df.columns:
                    pt = PowerTransformer(method='yeo-johnson', standardize=False)
                    df[col] = pt.fit_transform(df[[col]])
                    logging.info(f"Applied Yeo-Johnson transformation on column: {col}")
                else:
                    logging.warning(f"Skewed feature column not found: {col}")

            # Step 5: Encoding
            logging.info("Initiating encoding process")
            encoding_cfg = self.config.get('data_preprocessing', {}).get('encoding', {})
            label_cols = encoding_cfg.get('label_encoding', [])
            ohe_cols = encoding_cfg.get('ohe_hot_encoding', [])

            for col in label_cols:
                if col in df.columns:
                    le = LabelEncoder()
                    df[col] = le.fit_transform(df[col].astype(str))
                    logging.info(f"Applied Label Encoding on column: {col}")
                else:
                    logging.warning(f"Label encoding column not found: {col}")

            available_ohe_cols = [col for col in ohe_cols if col in df.columns]
            
            if available_ohe_cols:
                ohe = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
                ohe_array = ohe.fit_transform(df[available_ohe_cols])
                ohe_df = pd.DataFrame(
                    ohe_array,
                    columns=ohe.get_feature_names_out(available_ohe_cols),
                    index=df.index
                )
                df = pd.concat([df.drop(columns=available_ohe_cols), ohe_df], axis=1)
                logging.info(f"Applied OneHotEncoding on columns: {available_ohe_cols}")

            # Step 6: Drop multicollinearity columns (high VIF)
            drop_cols = self.config.get('data_preprocessing', {}).get('drop_multicollinearity_columns', [])
            if drop_cols:
                available_drop_cols = [col for col in drop_cols if col in df.columns]
                if available_drop_cols:
                    df = df.drop(columns=available_drop_cols, axis=1)
                    logging.info(f"Dropped multicollinearity columns: {available_drop_cols}")
                else:
                    logging.info(f"No multicollinearity columns found to drop")

            return df

        except Exception as e:
            raise CustomException(e, sys)


    def save_data(self, df, file_path):
        try:
            logging.info(f"Attempting to save processed data to: {file_path}")
            df.to_csv(file_path, index=False)
            logging.info(f"Saved processed data to: {file_path}")
        except Exception as e:
            logging.error(f"Error saving processed data to: {file_path} - {str(e)}")
            raise CustomException(e, sys)

    def run(self):
        try:
            logging.info("Starting data preprocessing pipeline")
            
            # Load FULL raw dataset (notebook approach)
            logging.info("Loading full raw dataset")
            df = load_data(self.raw_data_path)
            logging.info(f"Loaded raw data shape: {df.shape}")
            
            # Preprocess ALL data together (no train/test split yet)
            logging.info("Starting full dataset preprocessing")
            processed_df = self.preprocess_data(df)
            logging.info(f"Preprocessed data shape: {processed_df.shape}")
            
            # Save single preprocessed file
            # NOTE: Train/test split and SMOTE will be done in model_building.py
            self.save_data(processed_df, self.processed_file_path)
            logging.info("Data preprocessing pipeline completed successfully")
            logging.info("Note: Train/test split and SMOTE will be handled in model training")
            
            return processed_df
        except Exception as e:
            logging.error(f"Error in data preprocessing pipeline: {str(e)}")
            raise CustomException(e, sys)


if __name__ == "__main__":
    # Define paths
    PREPROCESSED_FILE_PATH = os.path.join(PROCESSED_DIR, "preprocessed_data.csv")
    
    preprocessor = DataPreprocessor(
        raw_data_path=RAW_FILE_PATH,
        processed_file_path=PREPROCESSED_FILE_PATH,
        config_path=CONFIG_FILE_PATH
    )
    preprocessor.run()