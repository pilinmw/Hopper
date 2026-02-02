"""
Data Analyzer

Intelligent data analysis and transformation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass


@dataclass
class DataSummary:
    """Summary of dataset"""
    total_rows: int
    total_columns: int
    columns: List[str]
    dtypes: Dict[str, str]
    categories: Dict[str, List[Any]]  # Categorical columns and their values
    date_range: Optional[Tuple[str, str]] = None
    numeric_columns: List[str] = None
    
    def to_dict(self):
        return {
            'total_rows': self.total_rows,
            'total_columns': self.total_columns,
            'columns': self.columns,
            'dtypes': self.dtypes,
            'categories': self.categories,
            'date_range': self.date_range,
            'numeric_columns': self.numeric_columns or []
        }


class DataAnalyzer:
    """Analyze and transform data based on user requests"""
    
    def __init__(self, dataframe: pd.DataFrame):
        """
        Initialize analyzer
        
        Args:
            dataframe: DataFrame to analyze
        """
        self.df = dataframe.copy()
        self.original_df = dataframe.copy()
        self.metadata = self._analyze_metadata()
        self.filter_history: List[Dict] = []
    
    def _analyze_metadata(self) -> DataSummary:
        """Analyze dataset and extract metadata"""
        # Get basic info
        total_rows = len(self.df)
        total_columns = len(self.df.columns)
        columns = self.df.columns.tolist()
        dtypes = {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        
        # Find categorical columns (object type or < 20 unique values)
        categories = {}
        for col in self.df.columns:
            if self.df[col].dtype == 'object' or self.df[col].nunique() < 20:
                unique_values = self.df[col].dropna().unique().tolist()
                if len(unique_values) <= 50:  # Limit to 50 categories
                    categories[col] = unique_values[:50]
        
        # Find date range
        date_range = None
        date_columns = self.df.select_dtypes(include=['datetime64']).columns
        if len(date_columns) > 0:
            first_date_col = date_columns[0]
            min_date = self.df[first_date_col].min()
            max_date = self.df[first_date_col].max()
            date_range = (str(min_date), str(max_date))
        
        # Find numeric columns
        numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        return DataSummary(
            total_rows=total_rows,
            total_columns=total_columns,
            columns=columns,
            dtypes=dtypes,
            categories=categories,
            date_range=date_range,
            numeric_columns=numeric_columns
        )
    
    def get_summary(self) -> Dict:
        """Get data summary for agent context"""
        return self.metadata.to_dict()
    
    def apply_filter(self, column: str, value: Any, operator: str = 'equals') -> pd.DataFrame:
        """
        Apply filter to data
        
        Args:
            column: Column to filter
            value: Value to filter by
            operator: Filter operator ('equals', 'contains', 'greater', 'less')
            
        Returns:
            Filtered DataFrame
        """
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in data")
        
        # Record filter
        self.filter_history.append({
            'column': column,
            'value': value,
            'operator': operator
        })
        
        # Apply filter
        if operator == 'equals':
            self.df = self.df[self.df[column] == value]
        elif operator == 'contains':
            self.df = self.df[self.df[column].astype(str).str.contains(str(value), case=False, na=False)]
        elif operator == 'greater':
            self.df = self.df[self.df[column] > value]
        elif operator == 'less':
            self.df = self.df[self.df[column] < value]
        elif operator == 'not_equals':
            self.df = self.df[self.df[column] != value]
        
        # Update metadata
        self.metadata = self._analyze_metadata()
        
        return self.df
    
    def apply_filters(self, filters: List[Dict]) -> pd.DataFrame:
        """
        Apply multiple filters
        
        Args:
            filters: List of filter dicts with 'column', 'value', 'operator'
            
        Returns:
            Filtered DataFrame
        """
        for filter_dict in filters:
            self.apply_filter(
                filter_dict['column'],
                filter_dict['value'],
                filter_dict.get('operator', 'equals')
            )
        
        return self.df
    
    def create_pivot(self, 
                     rows: List[str], 
                     columns: List[str], 
                     values: str,
                     aggfunc: str = 'sum') -> pd.DataFrame:
        """
        Create pivot table
        
        Args:
            rows: Row dimension columns
            columns: Column dimension columns
            values: Values column to aggregate
            aggfunc: Aggregation function ('sum', 'mean', 'count', 'min', 'max')
            
        Returns:
            Pivot table DataFrame
        """
        # Validate columns
        all_cols = rows + columns + [values]
        for col in all_cols:
            if col not in self.df.columns:
                raise ValueError(f"Column '{col}' not found")
        
        # Create pivot
        pivot = pd.pivot_table(
            self.df,
            index=rows,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
            fill_value=0
        )
        
        return pivot
    
    def group_by(self, columns: List[str], agg_dict: Dict[str, str]) -> pd.DataFrame:
        """
        Group by columns and aggregate
        
        Args:
            columns: Columns to group by
            agg_dict: Aggregation dictionary {column: function}
            
        Returns:
            Grouped DataFrame
        """
        return self.df.groupby(columns).agg(agg_dict).reset_index()
    
    def get_preview(self, rows: int = 10) -> Dict:
        """Get data preview for display"""
        preview_df = self.df.head(rows)
        
        return {
            'columns': preview_df.columns.tolist(),
            'data': preview_df.to_dict('records'),
            'total_rows': len(self.df),
            'showing_rows': len(preview_df)
        }
    
    def suggest_visualizations(self) -> List[Dict]:
        """Suggest appropriate visualizations based on data"""
        suggestions = []
        
        # If we have categories and numeric values
        if self.metadata.categories and self.metadata.numeric_columns:
            cat_cols = list(self.metadata.categories.keys())
            num_cols = self.metadata.numeric_columns
            
            # Bar chart suggestion
            suggestions.append({
                'type': 'bar',
                'title': f'{num_cols[0]} by {cat_cols[0]}',
                'x': cat_cols[0],
                'y': num_cols[0]
            })
            
            # If multiple numeric columns, suggest grouped bar
            if len(num_cols) > 1:
                suggestions.append({
                    'type': 'grouped_bar',
                    'title': f'Comparison of {num_cols[0]} and {num_cols[1]}',
                    'x': cat_cols[0],
                    'y': num_cols[:2]
                })
        
        # If we have date columns
        if self.metadata.date_range:
            date_cols = self.df.select_dtypes(include=['datetime64']).columns.tolist()
            if date_cols and self.metadata.numeric_columns:
                suggestions.append({
                    'type': 'line',
                    'title': f'{self.metadata.numeric_columns[0]} over time',
                    'x': date_cols[0],
                    'y': self.metadata.numeric_columns[0]
                })
        
        # Pie chart for single category
        if len(self.metadata.categories) > 0 and self.metadata.numeric_columns:
            cat_col = list(self.metadata.categories.keys())[0]
            if len(self.metadata.categories[cat_col]) <= 10:
                suggestions.append({
                    'type': 'pie',
                    'title': f'Distribution of {self.metadata.numeric_columns[0]} by {cat_col}',
                    'labels': cat_col,
                    'values': self.metadata.numeric_columns[0]
                })
        
        return suggestions
    
    def reset(self):
        """Reset to original data"""
        self.df = self.original_df.copy()
        self.filter_history = []
        self.metadata = self._analyze_metadata()
    
    def get_current_data(self) -> pd.DataFrame:
        """Get current filtered/transformed data"""
        return self.df.copy()
    
    def describe_current_state(self) -> str:
        """Get human-readable description of current data state"""
        filters_desc = ""
        if self.filter_history:
            filters_desc = "\nFilters applied:\n"
            for f in self.filter_history:
                filters_desc += f"  - {f['column']} {f['operator']} {f['value']}\n"
        
        return f"""Current data state:
- Rows: {len(self.df):,}
- Columns: {len(self.df.columns)}
{filters_desc}"""
