"""
Excel Merger

Merge multiple document sources (Excel, CSV, Word, PDF) into a single Excel file
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.parser_factory import ParserFactory
from cleaners.data_cleaner import DataCleaner, CleaningConfig


class ExcelMerger:
    """Merge multiple document files into one Excel workbook"""
    
    def __init__(self, auto_clean: bool = False, cleaning_config: Optional[CleaningConfig] = None):
        """
        Initialize the merger
        
        Args:
            auto_clean: Automatically clean data before merging
            cleaning_config: Configuration for data cleaning
        """
        self.sources = []  # List of parsed data from each file
        self.file_paths = []  # Original file paths
        self.auto_clean = auto_clean
        self.cleaning_config = cleaning_config or CleaningConfig()

        
    def add_file(self, file_path: str) -> bool:
        """
        Add a file to the merge queue
        
        Args:
            file_path: Path to the file to add
            
        Returns:
            True if successfully added, False otherwise
        """
        try:
            print(f"  📄 Processing: {Path(file_path).name}")
            
            # Create parser and parse file
            parser = ParserFactory.create_parser(file_path)
            data = parser.parse()
            
            # Store parsed data
            self.sources.append(data)
            self.file_paths.append(file_path)
            
            # Show quick stats
            tables = data['content'].get('tables', [])
            print(f"     ✓ Extracted {len(tables)} table(s)")
            
            return True
            
        except Exception as e:
            print(f"     ✗ Error: {e}")
            return False
    
    def add_files(self, file_paths: List[str]) -> int:
        """
        Add multiple files at once
        
        Args:
            file_paths: List of file paths
            
        Returns:
            Number of successfully added files
        """
        success_count = 0
        for file_path in file_paths:
            if self.add_file(file_path):
                success_count += 1
        return success_count
    
    def merge_to_excel(self, output_path: str) -> bool:
        """
        Merge all added files into a single Excel workbook
        
        Args:
            output_path: Path for the output Excel file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.sources:
            print("❌ Error: No files to merge")
            return False
        
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"\n📝 Merging {len(self.sources)} file(s) into Excel...")
            
            # Create Excel writer
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                sheet_count = 0
                
                # Process each source file
                for idx, (data, file_path) in enumerate(zip(self.sources, self.file_paths), 1):
                    file_name = Path(file_path).stem  # Filename without extension
                    file_format = data['metadata']['file_format']
                    tables = data['content'].get('tables', [])
                    
                    print(f"  {idx}. {file_name} ({file_format}): {len(tables)} table(s)")
                    
                    # Write each table as a separate sheet
                    for table_idx, df in enumerate(tables):
                        # Clean data if enabled
                        if self.auto_clean:
                            print(f"     🧹 Cleaning table {table_idx + 1}...")
                            cleaner = DataCleaner(df, self.cleaning_config)
                            df = cleaner.clean()
                        
                        # Generate sheet name
                        if len(tables) == 1:
                            sheet_name = f"{file_name}"
                        else:
                            sheet_name = f"{file_name}_T{table_idx + 1}"
                        
                        # Excel sheet names must be <= 31 characters
                        sheet_name = sheet_name[:31]
                        
                        # Write to Excel
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        sheet_count += 1
                        
                        print(f"     → Sheet: '{sheet_name}' ({df.shape[0]} rows × {df.shape[1]} cols)")
                
                # Create summary sheet
                self._create_summary_sheet(writer, sheet_count)
            
            # Get output file size
            file_size = output_file.stat().st_size
            file_size_kb = round(file_size / 1024, 2)
            
            print(f"\n✅ Merge complete!")
            print(f"   📁 Output: {output_path}")
            print(f"   📊 Sheets: {sheet_count} data + 1 summary = {sheet_count + 1} total")
            print(f"   💾 Size: {file_size_kb} KB")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Merge failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_summary_sheet(self, writer: pd.ExcelWriter, total_sheets: int):
        """
        Create a summary sheet with metadata about all merged files
        
        Args:
            writer: Excel writer object
            total_sheets: Total number of data sheets created
        """
        summary_data = []
        
        for data, file_path in zip(self.sources, self.file_paths):
            metadata = data['metadata']
            metrics = data['metrics']
            tables = data['content'].get('tables', [])
            
            # Calculate total rows
            total_rows = sum(len(df) for df in tables)
            
            summary_data.append({
                'Source File': metadata['file_name'],
                'Format': metadata['file_format'].upper(),
                'Tables': len(tables),
                'Total Rows': total_rows,
                'File Size (MB)': metadata['file_size_mb'],
                'Status': '✓ Merged'
            })
        
        # Add merge metadata
        summary_data.append({
            'Source File': '--- MERGE INFO ---',
            'Format': '',
            'Tables': '',
            'Total Rows': '',
            'File Size (MB)': '',
            'Status': ''
        })
        
        summary_data.append({
            'Source File': 'Total Files Merged',
            'Format': len(self.sources),
            'Tables': total_sheets,
            'Total Rows': sum(row['Total Rows'] for row in summary_data[:-2]),
            'File Size (MB)': '',
            'Status': ''
        })
        
        summary_data.append({
            'Source File': 'Merge Timestamp',
            'Format': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Tables': '',
            'Total Rows': '',
            'File Size (MB)': '',
            'Status': ''
        })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"     → Sheet: 'Summary' (metadata)")


def main():
    """Test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Merge multiple documents into Excel')
    parser.add_argument(
        '--files',
        type=str,
        required=True,
        help='Comma-separated list of file paths'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/output/merged_result.xlsx',
        help='Output Excel file path'
    )
    
    args = parser.parse_args()
    
    # Parse file list
    file_list = [f.strip() for f in args.files.split(',')]
    
    print("=" * 60)
    print("🔀 Multi-File Excel Merger")
    print("=" * 60)
    print(f"\n📥 Input: {len(file_list)} file(s)")
    
    # Create merger
    merger = ExcelMerger()
    
    # Add files
    success_count = merger.add_files(file_list)
    
    if success_count == 0:
        print("\n❌ No files were successfully processed")
        return 1
    
    if success_count < len(file_list):
        print(f"\n⚠️  Warning: Only {success_count}/{len(file_list)} files processed successfully")
    
    # Merge to Excel
    if merger.merge_to_excel(args.output):
        print("\n" + "=" * 60)
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
