# 🏭 智能文档工厂 (Smart Document Factory)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

> **通用文档智能转换平台** - 支持多格式输入，智能数据提炼，多风格输出

## 💡 核心理念

不只是格式转换工具，而是一个**懂业务的文档生产流水线**：
- 📥 **投入原材料**：Excel、Word、PDF、图片等任意格式
- 🧠 **智能加工**：自动提炼数据、分类整理、提取关键信息
- 🎨 **多方案生成**：一次输入，生成多种风格的输出供选择
- 📤 **按需交付**：输出为 PPT、Word、Excel、PDF 等目标格式

## ✨ 核心特性

### 📊 智能解析引擎
- 自动识别文档结构和数据类型
- 支持 Excel、CSV、Word、PDF 等多种格式
- 智能提取关键指标和数据关系

### 🎨 多风格生成（当前支持 PPT）
一键生成 3 种差异化方案：
- **方案 A：稳重商务风** - 蓝白配色，数据表格为主，适合正式汇报
- **方案 B：视觉冲击风** - 深色背景，大面积图表，适合路演展示
- **方案 C：详尽分析风** - 信息图风格，层次清晰，适合研究报告

### ⚡ 性能表现
- 端到端处理时间：**5-10 秒**（实测）
- 文件大小：约 **38KB/个 PPT**
- 支持批量处理

### 🎯 场景化能力
- 金融行业：业绩报告、投资分析
- 咨询行业：数据可视化、客户提案
- 人力资源：简历汇总、员工数据分析
- 法律合规：合同批量生成、清单核对

## 项目结构

```
smart-doc-factory/
├── src/                    # 源代码
│   ├── parsers/           # Excel 解析器
│   ├── generators/        # PPT 生成器
│   └── styles/            # 风格配置
├── templates/             # PPT 母版模板
├── data/
│   ├── input/            # 测试输入文件
│   └── output/           # 生成的文件
├── tests/                # 单元测试
└── requirements.txt      # 依赖配置
```

## 快速开始

### 1. 安装依赖

```bash
cd smart-doc-factory
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 2. 运行示例

```bash
python src/main.py --input data/input/sample.xlsx
```

## 当前状态

🚧 **技术验证阶段** - 正在实现核心 Excel → PPT 转换流程

## 开发计划

- [x] 项目架构设计
- [/] 技术验证原型
- [ ] MVP 开发
- [ ] 预览系统
- [ ] Web 界面

## 🚀 快速开始

### 安装依赖

```bash
cd smart-doc-factory
pip install -r requirements.txt
```

### 运行示例

```bash
# 使用内置测试数据
python src/main.py --input data/input/sample.xlsx

# 使用自己的数据
python src/main.py --input /path/to/your/file.xlsx --output ./my_reports
```

### 输出结果

生成 3 个不同风格的 PPT 文件：
- `report_conservative_[timestamp].pptx` (约 38KB)
- `report_visual_[timestamp].pptx` (约 38KB)
- `report_detailed_[timestamp].pptx` (约 38KB)

## 📋 使用示例

### 场景 1：金融行业周报

```python
from parsers.excel_parser import ExcelParser
from generators.ppt_generator import PPTGenerator

# 解析数据
parser = ExcelParser('fund_report.xlsx')
data = parser.parse()

# 生成视觉冲击风格的路演 PPT
gen = PPTGenerator(style='visual')
gen.add_title_slide("Q4 基金业绩报告", "2024年第四季度")
gen.add_data_slide("关键指标", data)
gen.save('output/q4_report.pptx')
```

### 场景 2：批量处理

```bash
# 处理文件夹内所有 Excel 文件
for file in data/input/*.xlsx; do
    python src/main.py --input "$file"
done
```

## 🛣️ 未来规划

### V0.1（当前版本）✅
- [x] Excel → PPT（3 种风格）
- [x] 核心解析引擎
- [x] 命令行工具

### V0.2（计划中）🚧
- [ ] Web 界面（拖拽上传）
- [ ] 实时预览系统（HTML 版本）
- [ ] 用户微调（颜色、字体、图表类型）
- [ ] 更多输入格式支持
  - [ ] CSV 导入
  - [ ] Word 文档解析
  - [ ] PDF 表格提取

### V1.0（未来愿景）🌟
- [ ] **通用文档转换矩阵**
  - [ ] Word → Excel（信息提取）
  - [ ] PDF → Word（OCR + 格式保持）
  - [ ] Excel → Word（批量合同生成）
  - [ ] 图片 → 结构化数据
- [ ] **智能分类引擎**
  - [ ] 按维度自动分组（部门/时间/金额）
  - [ ] 异常数据标注
  - [ ] 趋势分析与预测
- [ ] **企业级功能**
  - [ ] 钉钉/飞书集成
  - [ ] 私有化部署
  - [ ] 自定义模板编辑器
  - [ ] API 接口

## 🤝 贡献

欢迎贡献代码、报告问题或提出新功能建议！

1. Fork 本仓库
2. 创建特性分支: `git checkout -b feature/AmazingFeature`
3. 提交更改: `git commit -m 'Add some AmazingFeature'`
4. 推送到分支: `git push origin feature/AmazingFeature`
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 感谢 [python-pptx](https://github.com/scanny/python-pptx) 提供的强大 PPT 操作能力
- 感谢 [pandas](https://pandas.pydata.org/) 提供的数据处理支持

## 📧 联系方式

- 项目主页: [GitHub](https://github.com/yanglingxiao/smart-doc-factory)
- 问题反馈: [Issues](https://github.com/yanglingxiao/smart-doc-factory/issues)

---

**Made with ❤️ by Smart Document Factory Team**


- **Python 3.10+**
- **pandas**: Excel 数据处理
- **python-pptx**: PowerPoint 生成
- **matplotlib**: 图表渲染
