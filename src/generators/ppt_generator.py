"""
PowerPoint Generator Module

Features:
1. Template-based PPT generation
2. Support multiple styles (conservative, visual, detailed)
3. Auto-insert data and charts
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
import pandas as pd
from typing import Dict, Any, List
from pathlib import Path


class StyleConfig:
    """PPT style configuration"""
    
    CONSERVATIVE = {
        'name': 'Option A: Conservative Business Style',
        'primary_color': (31, 78, 120),      # Dark blue
        'secondary_color': (79, 129, 189),   # Light blue
        'background': (255, 255, 255),       # White
        'font_color': (0, 0, 0),             # Black
        'emphasis': 'data_tables'            # Emphasize data tables
    }
    
    VISUAL = {
        'name': 'Option B: Visual Impact Style',
        'primary_color': (255, 87, 51),      # Orange-red
        'secondary_color': (255, 195, 0),    # Golden yellow
        'background': (33, 33, 33),          # Dark gray
        'font_color': (255, 255, 255),       # White
        'emphasis': 'large_charts'           # Emphasize large charts
    }
    
    DETAILED = {
        'name': 'Option C: Detailed Analysis Style',
        'primary_color': (46, 125, 50),      # Dark green
        'secondary_color': (129, 199, 132),  # Light green
        'background': (245, 245, 245),       # Light gray
        'font_color': (33, 33, 33),          # Dark gray
        'emphasis': 'infographics'           # Emphasize infographics
    }


class PPTGenerator:
    """PowerPoint generator"""
    
    def __init__(self, style: str = 'conservative'):
        """
        Initialize generator
        
        Args:
            style: Style type ('conservative', 'visual', 'detailed')
        """
        self.prs = Presentation()
        self.prs.slide_width = Inches(10)
        self.prs.slide_height = Inches(7.5)
        
        # Select style configuration
        style_map = {
            'conservative': StyleConfig.CONSERVATIVE,
            'visual': StyleConfig.VISUAL,
            'detailed': StyleConfig.DETAILED
        }
        self.style = style_map.get(style, StyleConfig.CONSERVATIVE)
        
    def add_title_slide(self, title: str, subtitle: str = None):
        """
        Add title slide
        
        Args:
            title: Main title
            subtitle: Subtitle
        """
        # Use blank layout
        blank_layout = self.prs.slide_layouts[6]
        slide = self.prs.slides.add_slide(blank_layout)
        
        # Add background color
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = self._rgb_tuple_to_color(self.style['background'])
        
        # Add title
        left = Inches(1)
        top = Inches(2.5)
        width = Inches(8)
        height = Inches(1.5)
        
        title_box = slide.shapes.add_textbox(left, top, width, height)
        text_frame = title_box.text_frame
        text_frame.text = title
        
        # Set title style
        p = text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(44)
        p.font.bold = True
        p.font.color.rgb = self._rgb_tuple_to_color(self.style['primary_color'])
        
        # Add subtitle
        if subtitle:
            sub_top = Inches(4.2)
            sub_box = slide.shapes.add_textbox(left, sub_top, width, Inches(0.8))
            sub_frame = sub_box.text_frame
            sub_frame.text = subtitle
            
            sub_p = sub_frame.paragraphs[0]
            sub_p.alignment = PP_ALIGN.CENTER
            sub_p.font.size = Pt(24)
            sub_p.font.color.rgb = self._rgb_tuple_to_color(self.style['font_color'])
        
        return slide
    
    def add_data_slide(self, title: str, df: pd.DataFrame):
        """
        Add data table slide
        
        Args:
            title: Title
            df: pandas DataFrame
        """
        blank_layout = self.prs.slide_layouts[6]
        slide = self.prs.slides.add_slide(blank_layout)
        
        # Background
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = self._rgb_tuple_to_color(self.style['background'])
        
        # Title
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(0.6))
        title_frame = title_box.text_frame
        title_frame.text = title
        p = title_frame.paragraphs[0]
        p.font.size = Pt(32)
        p.font.bold = True
        p.font.color.rgb = self._rgb_tuple_to_color(self.style['primary_color'])
        
        # Table
        rows, cols = min(df.shape[0] + 1, 10), min(df.shape[1], 6)  # Limit size
        left = Inches(0.5)
        top = Inches(1.5)
        width = Inches(9)
        height = Inches(5)
        
        table = slide.shapes.add_table(rows, cols, left, top, width, height).table
        
        # Fill header
        for col_idx, col_name in enumerate(df.columns[:cols]):
            cell = table.cell(0, col_idx)
            cell.text = str(col_name)
            cell.fill.solid()
            cell.fill.fore_color.rgb = self._rgb_tuple_to_color(self.style['primary_color'])
            cell.text_frame.paragraphs[0].font.color.rgb = self._rgb_tuple_to_color(
                self.style['background']
            )
            cell.text_frame.paragraphs[0].font.bold = True
        
        # Fill data
        for row_idx in range(min(rows - 1, df.shape[0])):
            for col_idx in range(cols):
                cell = table.cell(row_idx + 1, col_idx)
                value = df.iloc[row_idx, col_idx]
                cell.text = str(value) if pd.notna(value) else ""
                cell.text_frame.paragraphs[0].font.size = Pt(12)
        
        return slide
    
    def add_chart_slide(self, title: str, data: Dict[str, List], chart_type: str = 'bar'):
        """
        Add chart slide
        
        Args:
            title: Title
            data: Chart data {'categories': [...], 'series': {'Series1': [...], ...}}
            chart_type: Chart type ('bar', 'line', 'pie')
        """
        blank_layout = self.prs.slide_layouts[6]
        slide = self.prs.slides.add_slide(blank_layout)
        
        # Background
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = self._rgb_tuple_to_color(self.style['background'])
        
        # Title
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(0.6))
        title_frame = title_box.text_frame
        title_frame.text = title
        p = title_frame.paragraphs[0]
        p.font.size = Pt(32)
        p.font.bold = True
        p.font.color.rgb = self._rgb_tuple_to_color(self.style['primary_color'])
        
        # Chart data
        chart_data = CategoryChartData()
        chart_data.categories = data.get('categories', [])
        
        for series_name, values in data.get('series', {}).items():
            chart_data.add_series(series_name, values)
        
        # Add chart
        x, y, cx, cy = Inches(1), Inches(2), Inches(8), Inches(5)
        
        chart_type_map = {
            'bar': XL_CHART_TYPE.COLUMN_CLUSTERED,
            'line': XL_CHART_TYPE.LINE,
            'pie': XL_CHART_TYPE.PIE
        }
        
        chart = slide.shapes.add_chart(
            chart_type_map.get(chart_type, XL_CHART_TYPE.COLUMN_CLUSTERED),
            x, y, cx, cy, chart_data
        ).chart
        
        return slide
    
    def save(self, output_path: str):
        """
        Save PPT file
        
        Args:
            output_path: Output file path
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        self.prs.save(str(output_file))
        print(f"✅ PPT saved: {output_path}")
    
    def _rgb_tuple_to_color(self, rgb_tuple):
        """Convert RGB tuple to RGBColor"""
        from pptx.dml.color import RGBColor
        return RGBColor(*rgb_tuple)


def main():
    """Test function"""
    # Generate three style examples
    for style_name in ['conservative', 'visual', 'detailed']:
        gen = PPTGenerator(style=style_name)
        
        # Add title slide
        gen.add_title_slide(
            f"Quarterly Performance Report - {gen.style['name']}", 
            "2024 Q4"
        )
        
        # Add data slide
        sample_df = pd.DataFrame({
            'Metric': ['Return Rate', 'Volatility', 'Sharpe Ratio'],
            'Q3': [8.5, 12.3, 0.69],
            'Q4': [12.8, 15.1, 0.85]
        })
        gen.add_data_slide("Key Metrics Comparison", sample_df)
        
        # Add chart slide
        chart_data = {
            'categories': ['Jan', 'Feb', 'Mar'],
            'series': {
                'Return Rate': [5.2, 7.8, 12.8],
                'Benchmark': [4.1, 6.5, 9.2]
            }
        }
        gen.add_chart_slide("Monthly Return Trend", chart_data, chart_type='line')
        
        # Save
        gen.save(f'data/output/demo_{style_name}.pptx')


if __name__ == '__main__':
    main()
