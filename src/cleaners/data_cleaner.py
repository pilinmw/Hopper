"""
Data Cleaner

Intelligent data cleaning and preprocessing
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import re


@dataclass
class CleaningConfig:
    """Configuration for data cleaning operations"""
    
    # Duplicate handling
    remove_duplicates: bool = True
    duplicate_subset: Optional[List[str]] = None
    keep_duplicate: str = 'first'  # 'first' or 'last'
    
    # Null handling
    handle_nulls: bool = True
    null_threshold: float = 0.5  # Drop column if >50% null
    fill_strategy: str = 'mean'  # 'mean', 'median', 'mode', 'ffill', 'bfill', 'drop'
    
    # Type inference
    infer_types: bool = True
    parse_dates: bool = True
    
    # Column normalization
    normalize_names: bool = True
    
    # Outlier detection
    detect_outliers: bool = False
    outlier_method: str = 'iqr'  # 'iqr' or 'zscore'


@dataclass
class CleaningReport:
    """Report of cleaning operations performed"""
    
    original_shape: tuple = (0, 0)
    final_shape: tuple = (0, 0)
    
    duplicates_removed: int = 0
    nulls_filled: Dict[str, int] = field(default_factory=dict)
    columns_dropped: List[str] = field(default_factory=list)
    types_converted: Dict[str, str] = field(default_factory=dict)
    columns_renamed: Dict[str, str] = field(default_factory=dict)
    outliers_detected: int = 0
    
    def __str__(self):
        """String representation of report"""
        lines = [
            "=" * 60,
            "Data Cleaning Report",
            "=" * 60,
            f"Shape: {self.original_shape} → {self.final_shape}",
            ""
        ]
        
        if self.duplicates_removed > 0:
            lines.append(f"✓ Removed {self.duplicates_removed} duplicate rows")
        
        if self.nulls_filled:
            lines.append(f"✓ Filled nulls in {len(self.nulls_filled)} columns:")
            for col, count in self.nulls_filled.items():
                lines.append(f"  - {col}: {count} values")
        
        if self.columns_dropped:
            lines.append(f"✓ Dropped {len(self.columns_dropped)} columns:")
            for col in self.columns_dropped:
                lines.append(f"  - {col}")
        
        if self.types_converted:
            lines.append(f"✓ Converted data types in {len(self.types_converted)} columns:")
            for col, dtype in self.types_converted.items():
                lines.append(f"  - {col}: {dtype}")
        
        if self.columns_renamed:
            lines.append(f"✓ Renamed {len(self.columns_renamed)} columns")
        
        if self.outliers_detected > 0:
            lines.append(f"✓ Detected {self.outliers_detected} outliers")
        
        lines.append("=" * 60)
        return "\n".join(lines)


class DataCleaner:
    """Intelligent data cleaner for DataFrames"""
    
    def __init__(self, df: pd.DataFrame, config: Optional[CleaningConfig] = None):
        """
        Initialize data cleaner
        
        Args:
            df: DataFrame to clean
            config: Cleaning configuration
        """
        self.df = df.copy()
        self.config = config or CleaningConfig()
        self.report = CleaningReport()
        self.report.original_shape = df.shape
    
    def clean(self) -> pd.DataFrame:
        """
        Apply all cleaning operations
        
        Returns:
            Cleaned DataFrame
        """
        print("\n🧹 Starting data cleaning...")
        
        if self.config.remove_duplicates:
            self.remove_duplicates()
        
        if self.config.handle_nulls:
            self.handle_nulls()
        
        if self.config.normalize_names:
            self.normalize_columns()
        
        if self.config.infer_types:
            self.infer_types()
        
        if self.config.detect_outliers:
            self.detect_outliers()
        
        self.report.final_shape = self.df.shape
        print("\n✅ Cleaning complete!")
        print(self.report)
        
        return self.df
    
    def remove_duplicates(self):
        """Remove duplicate rows"""
        initial_count = len(self.df)
        
        self.df = self.df.drop_duplicates(
            subset=self.config.duplicate_subset,
            keep=self.config.keep_duplicate
        )
        
        removed = initial_count - len(self.df)
        self.report.duplicates_removed = removed
        
        if removed > 0:
            print(f"  ✓ Removed {removed} duplicate rows")
    
    def handle_nulls(self):
        """Handle missing values"""
        # Drop columns with too many nulls
        null_ratio = self.df.isnull().sum() / len(self.df)
        cols_to_drop = null_ratio[null_ratio > self.config.null_threshold].index.tolist()
        
        if cols_to_drop:
            self.df = self.df.drop(columns=cols_to_drop)
            self.report.columns_dropped.extend(cols_to_drop)
            print(f"  ✓ Dropped {len(cols_to_drop)} columns with >{self.config.null_threshold*100}% nulls")
        
        # Fill remaining nulls
        for col in self.df.columns:
            null_count = self.df[col].isnull().sum()
            
            if null_count == 0:
                continue
            
            if self.config.fill_strategy == 'drop':
                # Drop rows with nulls
                self.df = self.df.dropna(subset=[col])
            elif self.config.fill_strategy == 'mean' and pd.api.types.is_numeric_dtype(self.df[col]):
                self.df[col] = self.df[col].fillna(self.df[col].mean())
            elif self.config.fill_strategy == 'median' and pd.api.types.is_numeric_dtype(self.df[col]):
                self.df[col] = self.df[col].fillna(self.df[col].median())
            elif self.config.fill_strategy == 'mode':
                mode_val = self.df[col].mode()
                if len(mode_val) > 0:
                    self.df[col] = self.df[col].fillna(mode_val[0])
            elif self.config.fill_strategy == 'ffill':
                self.df[col] = self.df[col].fillna(method='ffill')
            elif self.config.fill_strategy == 'bfill':
                self.df[col] = self.df[col].fillna(method='bfill')
            else:
                # Default: fill with empty string or 0
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    self.df[col] = self.df[col].fillna(0)
                else:
                    self.df[col] = self.df[col].fillna('')
            
            self.report.nulls_filled[col] = null_count
        
        if self.report.nulls_filled:
            print(f"  ✓ Filled nulls in {len(self.report.nulls_filled)} columns")
    
    def normalize_columns(self):
        """Normalize column names to snake_case"""
        renamed = {}
        
        for col in self.df.columns:
            # Convert to snake_case
            new_name = re.sub(r'[^\w\s]', '', col)  # Remove special chars
            new_name = re.sub(r'\s+', '_', new_name.strip())  # Replace spaces
            new_name = new_name.lower()
            
            if new_name != col:
                renamed[col] = new_name
        
        if renamed:
            self.df = self.df.rename(columns=renamed)
            self.report.columns_renamed = renamed
            print(f"  ✓ Normalized {len(renamed)} column names")
    
    def infer_types(self):
        """Infer and convert data types"""
        for col in self.df.columns:
            # Try to convert to numeric
            if self.df[col].dtype == 'object':
                try:
                    # Try converting to numeric
                    converted = pd.to_numeric(self.df[col], errors='coerce')
                    
                    # If most values converted successfully, use it
                    if converted.notna().sum() / len(converted) > 0.8:
                        original_type = str(self.df[col].dtype)
                        self.df[col] = converted
                        self.report.types_converted[col] = f"{original_type} → numeric"
                
                except:
                    pass
                
                # Try parsing dates
                if self.config.parse_dates:
                    try:
                        converted = pd.to_datetime(self.df[col], errors='coerce')
                        
                        if converted.notna().sum() / len(converted) > 0.8:
                            original_type = str(self.df[col].dtype)
                            self.df[col] = converted
                            self.report.types_converted[col] = f"{original_type} → datetime"
                    except:
                        pass
        
        if self.report.types_converted:
            print(f"  ✓ Converted {len(self.report.types_converted)} column types")
    
    def detect_outliers(self):
        """Detect outliers in numeric columns"""
        outlier_count = 0
        
        for col in self.df.select_dtypes(include=[np.number]).columns:
            if self.config.outlier_method == 'iqr':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = ((self.df[col] < lower_bound) | (self.df[col] > upper_bound))
                outlier_count += outliers.sum()
                
                # Mark outliers (add a flag column)
                if outliers.sum() > 0:
                    self.df[f'{col}_outlier'] = outliers
        
        self.report.outliers_detected = outlier_count
        
        if outlier_count > 0:
            print(f"  ✓ Detected {outlier_count} outliers")
