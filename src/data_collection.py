import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class DataCollection:
    def __init__(
            self
    ) -> None:
        self.file_name = PROJECT_ROOT / "data/bulacan_camanava_raw_social_media.csv"
        print(self.file_name)

    def collect_data(
            self
    ) -> pd.DataFrame:
        df = pd.read_csv(
            self.file_name, parse_dates=["date"]
        )
        df["text"] = df["text"].fillna("").astype(str).str.strip()
        df = df[df["text"].str.len() > 0].reset_index(drop=True)

        if "parent_post_id" in df.columns:
            df["parent_post_id"] = df["parent_post_id"].fillna("")

        print(f"Rows to process: {len(df):,}")
        print(f"Loaded {len(df):,} raw rows")
        print(f"Date range: {df.index.min()} → {df.index.max()}")
        print(f"Columns: {list(df.columns)}")

        return df