import os
import sys
import pandas as pd
import joblib
import warnings
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE

# Suppress specific warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='sklearn')
warnings.filterwarnings('ignore', category=UserWarning, module='xgboost')
warnings.filterwarnings('ignore', category=UserWarning, module='mlflow.types.utils')  # Schema hints
warnings.filterwarnings('ignore', category=UserWarning, module='mlflow.models.model')  # Deprecation warnings

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from config.paths_config import CONFIG_FILE_PATH, MODEL_OUTPUT_PATH, PROCESSED_DIR
from config.model_params import XGBOOST_FIXED_PARAMS, RANDOM_SEARCH_CV_CONFIG
from src.logger import logging
from src.custom_exception import CustomException
from utils.common_functions import read_yaml_file, load_data

import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature

class ModelTrainer:
    def __init__(self, preprocessed_file_path, model_output_path, config_path, use_hyperparameter_tuning=False):
        self.preprocessed_file_path = preprocessed_file_path
        self.model_output_path = model_output_path
        self.config_path = config_path
        self.use_hyperparameter_tuning = use_hyperparameter_tuning
        self.fixed_params = XGBOOST_FIXED_PARAMS
        self.random_search_cv_config = RANDOM_SEARCH_CV_CONFIG

    def load_split_processed_data(self):
        try:
            logging.info("Loading preprocessed data")
            df = load_data(self.preprocessed_file_path)
            logging.info(f"Loaded preprocessed data shape: {df.shape}")
            
            # Split features and target
            logging.info("Splitting features and target")
            X = df.drop(columns=['booking_status'], axis=1)
            y = df['booking_status']
            
            # Train-test split (matching notebook: test_size=0.2, random_state=42, stratify=y)
            logging.info("Performing train-test split (80-20, stratified)")
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            logging.info(f"Train shape: X={X_train.shape}, y={y_train.shape}")
            logging.info(f"Test shape: X={X_test.shape}, y={y_test.shape}")
            
            # Apply SMOTE on training data only
            logging.info("Applying SMOTE on training data")
            smote = SMOTE(sampling_strategy='auto', random_state=42)
            X_train, y_train = smote.fit_resample(X_train, y_train)
            logging.info(f"After SMOTE - Train shape: X={X_train.shape}, y={y_train.shape}")
            logging.info(f"Class distribution after SMOTE: {pd.Series(y_train).value_counts().to_dict()}")

            return X_train, X_test, y_train, y_test
        except Exception as e:
            logging.error(f"Error loading and splitting data: {str(e)}")
            raise CustomException(e, sys)

    def train_model(self, X_train, y_train):
        try:
            if self.use_hyperparameter_tuning:
                logging.info("Initiating model training with RandomizedSearchCV hyperparameter tuning")
                base_model = XGBClassifier(**self.fixed_params)
                
                # Add scoring='f1' for imbalanced classification
                random_search = RandomizedSearchCV(
                    estimator=base_model,
                    param_distributions=self.random_search_cv_config['param_distributions'],
                    n_iter=self.random_search_cv_config['n_iter'],
                    cv=self.random_search_cv_config['cv'],
                    scoring='f1',  # CRITICAL: Use F1 for imbalanced data
                    verbose=self.random_search_cv_config['verbose'],
                    random_state=self.random_search_cv_config['random_state'],
                    n_jobs=self.random_search_cv_config['n_jobs']
                )
                random_search.fit(X_train, y_train)
                
                logging.info(f"Best parameters found: {random_search.best_params_}")
                logging.info(f"Best cross-validation F1 score: {random_search.best_score_:.4f}")
                
                best_model = random_search.best_estimator_
                logging.info(f"Best tuned model: {best_model}")
                mlflow.log_params(random_search.best_params_)
                mlflow.log_metric("best_cv_f1", random_search.best_score_)

            else:
                # Simple XGBoost without tuning (notebook approach)
                logging.info("Training XGBoost without hyperparameter tuning (notebook approach)")
                best_model = XGBClassifier(**self.fixed_params)
                best_model.fit(X_train, y_train)
                logging.info("Model training completed")
            
            return best_model
        except Exception as e:
            logging.error(f"Error during model training: {str(e)}")
            raise CustomException(e, sys)
    
    def evaluate_model(self, model, X_test, y_test):
        try:
            logging.info("Initiating model evaluation on test data")
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]

            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred),
                'recall': recall_score(y_test, y_pred),
                'f1_score': f1_score(y_test, y_pred),
                'roc_auc': roc_auc_score(y_test, y_proba)
            }
            logging.info(f"Model evaluation metrics: {metrics}")
            return metrics
        except Exception as e:
            logging.error(f"Error during model evaluation: {str(e)}")
            raise CustomException(e, sys)
    
    def save_model(self, model):
        try:
            logging.info(f"Attempting to save the trained model to: {self.model_output_path}")

            os.makedirs(os.path.dirname(self.model_output_path), exist_ok=True)
            
            joblib.dump(model, self.model_output_path)
            
            logging.info(f"Model saved successfully to: {self.model_output_path}")
        except Exception as e:
            logging.error(f"Error saving the model: {str(e)}")
            raise CustomException(e, sys)
    
    def run(self):
        try:
            logging.info("Starting model training pipeline")
            
            with mlflow.start_run():
                X_train, X_test, y_train, y_test = self.load_split_processed_data()
                
                # Log parameters
                mlflow.log_param("use_hyperparameter_tuning", self.use_hyperparameter_tuning)
                mlflow.log_params(self.fixed_params)
                
                model = self.train_model(X_train, y_train)
                
                metrics = self.evaluate_model(model, X_test, y_test)
                
                # Log metrics
                mlflow.log_metrics(metrics)
                
                # Create signature and input example for MLflow
                logging.info("Creating model signature and input example")
                try:
                    # Ensure model has predict method before signature inference
                    y_pred_sample = model.predict(X_train[:10])
                    signature = infer_signature(X_train, y_pred_sample)
                    input_example = X_train.head(5)
                except Exception as e:
                    logging.warning(f"Could not infer signature: {e}. Logging model without signature.")
                    signature = None
                    input_example = None
                
                # Log model with signature and input example
                logging.info("Logging model to MLflow")
                mlflow.sklearn.log_model(
                    sk_model=model,
                    name="model",  # Updated from deprecated artifact_path
                    signature=signature,
                    input_example=input_example,
                    registered_model_name="hotel_reservation_xgboost" if signature else None
                )
                
                self.save_model(model)
            
            logging.info("Model training pipeline completed successfully")
            return metrics
        except Exception as e:
            logging.error(f"Error in model training pipeline: {str(e)}")
            raise CustomException(e, sys)
        
if __name__ == "__main__":
    # Use single preprocessed file
    PREPROCESSED_FILE_PATH = os.path.join(PROCESSED_DIR, "preprocessed_data.csv")
    
    trainer = ModelTrainer(
        preprocessed_file_path=PREPROCESSED_FILE_PATH,
        model_output_path=MODEL_OUTPUT_PATH,
        config_path=CONFIG_FILE_PATH,
        use_hyperparameter_tuning=False  # Set to True to enable RandomizedSearchCV
    )
    trainer.run()