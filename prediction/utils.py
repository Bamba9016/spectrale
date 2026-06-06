import joblib
import pickle
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / 'models' / 'svm_model.pkl'
SCALER_PATH = BASE_DIR / 'models' / 'scaler.pkl'
COLS_PATH = BASE_DIR / 'models' / 'selected_columns.pkl'

_model = None
_scaler = None
_selected_columns = None

def load_artifacts():
    global _model, _scaler, _selected_columns
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        _scaler = joblib.load(SCALER_PATH)
        with open(COLS_PATH, 'rb') as f:
            _selected_columns = pickle.load(f)
    return _model, _scaler, _selected_columns

# Le reste (predict_from_data) reste inchangé
def predict_from_data(df):
    model, scaler, cols = load_artifacts()
    missing = set(cols) - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes : {missing}")
    X = df[cols].copy()
    X = X.dropna()
    if X.empty:
        return None, None
    X_scaled = scaler.transform(X)
    y_pred = model.predict(X_scaled)
    y_proba = model.predict_proba(X_scaled)[:, 1]
    return y_pred, y_proba