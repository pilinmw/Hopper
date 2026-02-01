"""
Smart Document Factory - Main Program

Features:
- Support multiple document format inputs (Excel, CSV, Word, PDF)
- Intelligently parse and generate 3 PPT style options
- Automatic format detection
"""

import sys
from pathlib import Path
import argparse
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from parsers.parser_factory import ParserFactory
from generators.ppt_generator import PPTGenerator
import pandas as pd


def generate_reports(input_path: str, output_dir: str = 'data/output'):
    """
    Generate multi-style PPT reports from any format document
    
    Supported formats: Excel (.xlsx, .xls), CSV (.csv), Word (.docx), PDF (.pdf)
    
    Args:
        input_path: Input file path
        output_dir: Output directory
    """
    print("=" * 60)
    print("🚀 Smart Document Factory - Multi-Format Support")
    print("=" * 60)
    
    # 1. Auto-detect and create parser
    print(f"\n📖 Parsing file: {input_path}")
    
    try:
        parser = ParserFactory.create_parser(input_path)
    except ValueError as e:
        print(f"\n❌ {e}")
        supported = ', '.join(ParserFactory.get_supported_formats())
        print(f"💡 Tip: Supported formats include {supported}")
        return False
    
    # 2. Parse data
    data = parser.parse()
    metadata = data['metadata']
    metrics = data['metrics']
    content = data['content']
    
    print(f"✅ Parsing complete:")
    print(f"   - File format: {metadata['file_format']}")
    print(f"   - File size: {metadata['file_size_mb']} MB")
    
    # Display statistics
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            print(f"   - {key}: {value}")
    
    # 3. Extract table data
    tables = content.get('tables', [])
    
    if not tables:
        print("\n⚠️  Warning: No table data detected")
        print("💡 Tip: Current version mainly handles table data, plain text document support coming soon")
        return False
    
    print(f"   - Detected {len(tables)} table(s)")
    
    # Use first table to generate PPT
    df = tables[0]
    print(f"   - Using table 1: {df.shape[0]} rows x {df.shape[1]} columns")
    
    # 4. Generate three styles of PPT
    styles = ['conservative', 'visual', 'detailed']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print(f"\n🎨 Generating {len(styles)} PPT styles...")
    
    for style in styles:
        print(f"\n  ⚙️  Generating {style} style...")
        
        gen = PPTGenerator(style=style)
        
        # Title slide - use filename instead of sheet_name
        file_name = metadata['file_name']
        title = f"Data Analysis Report - {Path(file_name).stem}"
        subtitle = f"{datetime.now().strftime('%B %Y')}"
        
        gen.add_title_slide(title, subtitle)
        
        # Data overview slide
        overview_data = pd.DataFrame({
            'Metric': ['Data Source', 'Total Rows', 'Total Columns', 'Format Type'],
            'Value': [
                metadata['file_format'].upper(),
                metrics.get('row_count', len(df)),
                metrics.get('column_count', len(df.columns)),
                metadata['file_path'].split('.')[-1]
            ]
        })
        gen.add_data_slide("Data Overview", overview_data)
        
        # Data preview slide (show first few rows)
        if len(df) > 0:
            gen.add_data_slide("Data Preview", df.head(8))
        
        # If there's numeric data, generate charts
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            # Select first 3 numeric columns
            chart_cols = numeric_cols[:3]
            if chart_cols:
                chart_data = {
                    'categories': chart_cols,
                    'series': {
                        'Average': [df[col].mean() for col in chart_cols],
                        'Maximum': [df[col].max() for col in chart_cols]
                    }
                }
                gen.add_chart_slide("Numeric Metrics Comparison", chart_data, chart_type='bar')
        
        # Save file
        output_filename = f"report_{style}_{timestamp}.pptx"
        output_path = f"{output_dir}/{output_filename}"
        gen.save(output_path)
        
        # Get file size
        file_size = Path(output_path).stat().st_size
        file_size_kb = round(file_size / 1024, 2)
        print(f"     ✅ Generated: {output_filename} ({file_size_kb} KB)")
    
    print("\n" + "=" * 60)
    print("✨ All generation complete!")
    print(f"📁 Output directory: {output_dir}")
    print("=" * 60)
    
    return True


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Smart Document Factory - Excel to PPT')
    parser.add_argument(
        '--input',
        type=str,
        default='data/input/sample.xlsx',
        help='Input Excel file path'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/output',
        help='Output directory'
    )
    
    args = parser.parse_args()
    
    # Check input file
    if not Path(args.input).exists():
        print(f"❌ Error: File not found {args.input}")
        print("\n💡 Tip: Please place the Excel file in data/input/ directory")
        return 1
    
    # Generate reports
    try:
        generate_reports(args.input, args.output)
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
