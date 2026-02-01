"""
智能文档工厂 - 主程序

功能：
- 支持多种文档格式输入（Excel, CSV, Word, PDF）
- 智能解析并生成 3 种风格的 PPT 方案
- 自动格式检测
"""

import sys
from pathlib import Path
import argparse
from datetime import datetime

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent))

from parsers.parser_factory import ParserFactory
from generators.ppt_generator import PPTGenerator
import pandas as pd


def generate_reports(input_path: str, output_dir: str = 'data/output'):
    """
    从任意格式文档生成多风格 PPT 报告
    
    支持格式: Excel (.xlsx, .xls), CSV (.csv), Word (.docx), PDF (.pdf)
    
    Args:
        input_path: 输入文件路径
        output_dir: 输出目录
    """
    print("=" * 60)
    print("🚀 智能文档工厂 - 多格式支持版本")
    print("=" * 60)
    
    # 1. 自动检测并创建解析器
    print(f"\n📖 正在解析文件: {input_path}")
    
    try:
        parser = ParserFactory.create_parser(input_path)
    except ValueError as e:
        print(f"\n❌ {e}")
        supported = ', '.join(ParserFactory.get_supported_formats())
        print(f"💡 提示: 支持的格式包括 {supported}")
        return False
    
    # 2. 解析数据
    data = parser.parse()
    metadata = data['metadata']
    metrics = data['metrics']
    content = data['content']
    
    print(f"✅ 解析完成:")
    print(f"   - 文件格式: {metadata['file_format']}")
    print(f"   - 文件大小: {metadata['file_size_mb']} MB")
    
    # 显示统计信息
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            print(f"   - {key}: {value}")
    
    # 3. 提取表格数据
    tables = content.get('tables', [])
    
    if not tables:
        print("\n⚠️  警告: 未检测到表格数据")
        print("💡 提示: 当前版本主要处理表格数据，纯文本文档支持即将推出")
        return False
    
    print(f"   - 检测到 {len(tables)} 个表格")
    
    # 使用第一个表格生成 PPT
    df = tables[0]
    print(f"   - 使用表格 1: {df.shape[0]} 行 x {df.shape[1]} 列")
    
    # 4. 生成三种风格的 PPT
    styles = ['conservative', 'visual', 'detailed']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print(f"\n🎨 正在生成 {len(styles)} 种风格的 PPT...")
    
    for style in styles:
        print(f"\n  ⚙️  生成 {style} 风格...")
        
        gen = PPTGenerator(style=style)
        
        # 标题页 - 使用文件名而不是 sheet_name
        file_name = metadata['file_name']
        title = f"数据分析报告 - {Path(file_name).stem}"
        subtitle = f"{datetime.now().strftime('%Y年%m月')}"
        
        gen.add_title_slide(title, subtitle)
        
        # 数据概览页
        overview_data = pd.DataFrame({
            '指标': ['数据来源', '总行数', '总列数', '格式类型'],
            '数值': [
                metadata['file_format'].upper(),
                metrics.get('row_count', len(df)),
                metrics.get('column_count', len(df.columns)),
                metadata['file_path'].split('.')[-1]
            ]
        })
        gen.add_data_slide("数据概览", overview_data)
        
        # 数据表格页（显示前几行）
        if len(df) > 0:
            gen.add_data_slide("数据预览", df.head(8))
        
        # 如果有数值数据，生成图表
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            # 选取前3个数值列
            chart_cols = numeric_cols[:3]
            if chart_cols:
                chart_data = {
                    'categories': chart_cols,
                    'series': {
                        '平均值': [df[col].mean() for col in chart_cols],
                        '最大值': [df[col].max() for col in chart_cols]
                    }
                }
                gen.add_chart_slide("数值指标对比", chart_data, chart_type='bar')
        
        # 保存文件
        output_filename = f"report_{style}_{timestamp}.pptx"
        output_path = f"{output_dir}/{output_filename}"
        gen.save(output_path)
        
        # 获取文件大小
        file_size = Path(output_path).stat().st_size
        file_size_kb = round(file_size / 1024, 2)
        print(f"     ✅ 已生成: {output_filename} ({file_size_kb} KB)")
    
    print("\n" + "=" * 60)
    print("✨ 全部生成完成！")
    print(f"📁 输出目录: {output_dir}")
    print("=" * 60)
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='智能文档工厂 - Excel 转 PPT')
    parser.add_argument(
        '--input',
        type=str,
        default='data/input/sample.xlsx',
        help='输入 Excel 文件路径'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/output',
        help='输出目录'
    )
    
    args = parser.parse_args()
    
    # 检查输入文件
    if not Path(args.input).exists():
        print(f"❌ 错误: 文件不存在 {args.input}")
        print("\n💡 提示: 请先将 Excel 文件放到 data/input/ 目录")
        return 1
    
    # 生成报告
    try:
        generate_reports(args.input, args.output)
        return 0
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
