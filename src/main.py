"""
智能文档工厂 - 主程序

功能：
- 读取 Excel 文件
- 生成 3 种风格的 PPT 方案
- 对比输出效果
"""

import sys
from pathlib import Path
import argparse
from datetime import datetime

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent))

from parsers.excel_parser import ExcelParser
from generators.ppt_generator import PPTGenerator
import pandas as pd


def generate_reports(excel_path: str, output_dir: str = 'data/output'):
    """
    从 Excel 生成多风格 PPT 报告
    
    Args:
        excel_path: Excel 文件路径
        output_dir: 输出目录
    """
    print("=" * 60)
    print("🚀 智能文档工厂 - 技术验证原型")
    print("=" * 60)
    
    # 1. 解析 Excel
    print(f"\n📖 正在解析 Excel: {excel_path}")
    parser = ExcelParser(excel_path)
    data = parser.parse()
    metrics = parser.extract_metrics()
    
    print(f"✅ 解析完成:")
    print(f"   - 工作表数: {len(data)}")
    print(f"   - 数据行数: {metrics['row_count']}")
    print(f"   - 数据列数: {metrics['column_count']}")
    
    # 获取第一个工作表的数据
    df = parser.get_dataframe()
    
    # 2. 生成三种风格的 PPT
    styles = ['conservative', 'visual', 'detailed']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print(f"\n🎨 正在生成 {len(styles)} 种风格的 PPT...")
    
    for style in styles:
        print(f"\n  ⚙️  生成 {style} 风格...")
        
        gen = PPTGenerator(style=style)
        
        # 标题页
        gen.add_title_slide(
            "数据分析报告",
            f"{metrics['sheet_name']} - {datetime.now().strftime('%Y年%m月')}"
        )
        
        # 数据概览页
        overview_data = pd.DataFrame({
            '指标': ['总行数', '总列数', '数值列数'],
            '数值': [
                metrics['row_count'],
                metrics['column_count'],
                len(metrics['summary'])
            ]
        })
        gen.add_data_slide("数据概览", overview_data)
        
        # 数据表格页（显示前几行）
        if len(df) > 0:
            gen.add_data_slide("数据预览", df.head(8))
        
        # 如果有数值数据，生成图表
        if metrics['summary']:
            # 选取前3个数值列
            numeric_cols = list(metrics['summary'].keys())[:3]
            if numeric_cols:
                chart_data = {
                    'categories': numeric_cols,
                    'series': {
                        '平均值': [metrics['summary'][col]['mean'] for col in numeric_cols],
                        '最大值': [metrics['summary'][col]['max'] for col in numeric_cols]
                    }
                }
                gen.add_chart_slide("数值指标对比", chart_data, chart_type='bar')
        
        # 保存文件
        output_path = f"{output_dir}/report_{style}_{timestamp}.pptx"
        gen.save(output_path)
    
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
