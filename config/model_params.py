# Fixed XGBoost parameters (non-tunable)
XGBOOST_FIXED_PARAMS = {
    'eval_metric': 'logloss',
    'random_state': 42
}

# RandomizedSearchCV configuration with parameter distributions
RANDOM_SEARCH_CV_CONFIG = {
    'param_distributions': {
        'n_estimators': [100, 300, 500, 1000],
        'learning_rate': [0.01, 0.05, 0.1],
        'max_depth': [3, 5, 7],
        'subsample': [0.6, 0.8, 1.0],
        'colsample_bytree': [0.6, 0.8, 1.0]
    },
    'n_iter': 10,
    'cv': 5,
    'verbose': 2,
    'random_state': 42,
    'n_jobs': -1
}