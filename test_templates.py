#!/usr/bin/env python3
"""
Test Template System

Test the TemplateEngine functionality
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.mergers.excel_merger import ExcelMerger
from src.templates.template_engine import TemplateEngine, TemplateConfig

print("=" * 70)
print("🎨 Testing Template System")
print("=" * 70)

# Test files
test_files = [
    "data/input/sample.xlsx",
    "data/input/products.csv"
]

# Test template 1: Professional
print("\n1️⃣ Testing Professional Template...")
template1 = TemplateEngine("professional")
merger1 = ExcelMerger(template_engine=template1)
merger1.add_files(test_files)
merger1.merge_to_excel("data/output/template_professional.xlsx")
print("✅ Professional template applied")

# Test template 2: Modern
print("\n2️⃣ Testing Modern Template...")
template2 = TemplateEngine("modern")
merger2 = ExcelMerger(template_engine=template2)
merger2.add_files(test_files)
merger2.merge_to_excel("data/output/template_modern.xlsx")
print("✅ Modern template applied")

# Test template 3: Financial
print("\n3️⃣ Testing Financial Template...")
template3 = TemplateEngine("financial")
merger3 = ExcelMerger(template_engine=template3)
merger3.add_files(test_files)
merger3.merge_to_excel("data/output/template_financial.xlsx")
print("✅ Financial template applied")

# Test custom colors
print("\n4️⃣ Testing Custom Template...")
custom_config = TemplateConfig(
    primary_color="FF6B6B",
    secondary_color="4ECDC4",
    accent_color="FFE66D",
    header_bg="FFE5E5",
    company_name="Custom Corp"
)
template4 = TemplateEngine(config=custom_config)
merger4 = ExcelMerger(template_engine=template4)
merger4.add_files(test_files)
merger4.merge_to_excel("data/output/template_custom.xlsx")
print("✅ Custom template applied")

print("\n" + "=" * 70)
print("✅ All template tests complete!")
print("   Check data/output/ for generated files:")
print("   - template_professional.xlsx")
print("   - template_modern.xlsx")
print("   - template_financial.xlsx")
print("   - template_custom.xlsx")
print("=" * 70)
