"""Milestone 2/3: load raw CSVs and do a first inspection pass.

Nothing here transforms data — it only loads and reports. Cleaning logic
lives in clean.py so each stage stays independently testable.
"""

import pandas as pd
from src.utils.config import CONFIG, resolve_path
from src.utils.logger import get_logger

log = get_logger(__name__)


def _read_csv(filename: str) -> pd.DataFrame:
    raw_dir = resolve_path(CONFIG["paths"]["raw_dir"])
    path = raw_dir / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Expected raw file at {path} — check config.yaml `raw_files` "
            f"and make sure the CSV is placed in data/raw/."
        )
    df = pd.read_csv(path)
    log.info(f"Loaded {filename}: {df.shape[0]} rows x {df.shape[1]} cols")
    return df


def load_donors() -> pd.DataFrame:
    return _read_csv(CONFIG["raw_files"]["donors"])


def load_blood_banks() -> pd.DataFrame:
    return _read_csv(CONFIG["raw_files"]["blood_banks"])


def load_tn_blood_banks() -> pd.DataFrame:
    return _read_csv(CONFIG["raw_files"]["tn_blood_banks"])


def load_population() -> pd.DataFrame:
    return _read_csv(CONFIG["raw_files"]["population"])


def inspect(df: pd.DataFrame, name: str) -> None:
    """Quick console inspection report — used in notebooks/01_inspection."""
    print(f"\n{'='*60}\n{name}\n{'='*60}")
    print(f"Shape: {df.shape}")
    print(f"\nDtypes:\n{df.dtypes}")
    print(f"\nMissing values:\n{df.isna().sum()[df.isna().sum() > 0]}")
    print(f"\nDuplicate rows: {df.duplicated().sum()}")
    print(f"\nHead:\n{df.head(3)}")


if __name__ == "__main__":
    donors = load_donors()
    blood_banks = load_blood_banks()
    tn_blood_banks = load_tn_blood_banks()
    population = load_population()

    for df, name in [
        (donors, "Blood Donation Portal Dataset"),
        (blood_banks, "Blood Bank Directory"),
        (tn_blood_banks, "Tamil Nadu Blood Banks"),
        (population, "Population Dataset"),
    ]:
        inspect(df, name)
