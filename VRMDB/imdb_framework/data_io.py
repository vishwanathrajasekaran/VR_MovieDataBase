# data_io.py
import pandas as pd
from config import INPUT_EXCEL_PATH, OUTPUT_EXCEL_PATH, IMDB_ID_COLUMN

def read_input_csv() -> pd.DataFrame:
    df = pd.read_csv(INPUT_EXCEL_PATH)
    if IMDB_ID_COLUMN not in df.columns:
        raise ValueError(f"Column '{IMDB_ID_COLUMN}' not found in CSV")
    return df

def save_dataframe_csv(df: pd.DataFrame, path: str) -> str:
    df.to_csv(path, index=False)
    return path
