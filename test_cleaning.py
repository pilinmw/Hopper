#!/usr/bin/env python3
"""
Test Data Cleaning

Test the DataCleaner functionality
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cleaners.data_cleaner import DataCleaner, CleaningConfig
import pandas as pd

print("=" * 70)
print("🧪 Testing Data Cleaning Functionality")
print("=" * 70)

# Load messy data
print("\n1️⃣ Loading messy data...")
df = pd.read_csv('data/input/messy_data.csv')

print(f"\nOriginal data:")
print(df)
print(f"\nShape: {df.shape}")
print(f"Duplicates: {df.duplicated().sum()}")
print(f"Nulls: {df.isnull().sum().sum()}")

# Configure cleaning
print("\n2️⃣ Configuring data cleaner...")
config = CleaningConfig(
    remove_duplicates=True,
    handle_nulls=True,
    fill_strategy='median',
    normalize_names=True,
    infer_types=True
)

# Clean data
print("\n3️⃣ Cleaning data...")
cleaner = DataCleaner(df, config)
cleaned_df = cleaner.clean()

print(f"\nCleaned data:")
print(cleaned_df)
print(f"\nShape: {cleaned_df.shape}")
print(f"Column names: {list(cleaned_df.columns)}")
print(f"Data types:\n{cleaned_df.dtypes}")

print("\n" + "=" * 70)
print("✅ Data cleaning test complete!")
print("=" * 70)
