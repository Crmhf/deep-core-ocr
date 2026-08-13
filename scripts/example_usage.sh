#!/bin/bash
# Example usage script for Deep Core OCR skill

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "Deep Core OCR - Example Usage"
echo "=========================================="

# Example 1: Basic OCR
echo ""
echo "Example 1: Basic OCR"
echo "-------------------------------------------"
echo "Command:"
echo "  python3 $SCRIPT_DIR/ocr.py \\"
echo "    --image input/document.png \\"
echo "    --output output/document.txt"
echo ""
echo "To run this example, uncomment the lines below:"
# python3 "$SCRIPT_DIR/ocr.py" \
#   --image input/document.png \
#   --output output/document.txt

# Example 2: Specify provider
echo ""
echo "Example 2: Specify provider"
echo "-------------------------------------------"
echo "Command:"
echo "  python3 $SCRIPT_DIR/ocr.py \\"
echo "    --image input/document.png \\"
echo "    --provider qwen-vl \\"
echo "    --output output/document.txt"
echo ""
echo "To run this example, uncomment the lines below:"
# python3 "$SCRIPT_DIR/ocr.py" \
#   --image input/document.png \
#   --provider qwen-vl \
#   --output output/document.txt

# Example 3: Structured extraction
echo ""
echo "Example 3: Structured extraction"
echo "-------------------------------------------"
echo "Command:"
echo "  python3 $SCRIPT_DIR/ocr.py \\"
echo "    --image input/invoice.png \\"
echo "    --mode structured \\"
echo "    --prompt '提取发票编号、金额、日期、供应商，输出 JSON' \\"
echo "    --output output/invoice.json"
echo ""
echo "To run this example, uncomment the lines below:"
# python3 "$SCRIPT_DIR/ocr.py" \
#   --image input/invoice.png \
#   --mode structured \
#   --prompt "提取发票编号、金额、日期、供应商，输出 JSON" \
#   --output output/invoice.json

# Example 4: JSON output
echo ""
echo "Example 4: JSON output"
echo "-------------------------------------------"
echo "Command:"
echo "  python3 $SCRIPT_DIR/ocr.py \\"
echo "    --image input/document.png \\"
echo "    --format json \\"
echo "    --output output/document.json"
echo ""
echo "To run this example, uncomment the lines below:"
# python3 "$SCRIPT_DIR/ocr.py" \
#   --image input/document.png \
#   --format json \
#   --output output/document.json

# Example 5: Complex scene with MiniMax-M3
echo ""
echo "Example 5: Complex scene with MiniMax-M3"
echo "-------------------------------------------"
echo "Command:"
echo "  python3 $SCRIPT_DIR/ocr.py \\"
echo "    --image input/scene.png \\"
echo "    --provider minimax-m3 \\"
echo "    --output output/scene.txt"
echo ""
echo "To run this example, uncomment the lines below:"
# python3 "$SCRIPT_DIR/ocr.py" \
#   --image input/scene.png \
#   --provider minimax-m3 \
#   --output output/scene.txt

echo ""
echo "=========================================="
echo "For more information, see:"
echo "  - README.md for quick start"
echo "  - SKILL.md for full documentation"
echo "  - references/ocr-scenario-guide.md for scenario guide"
echo "=========================================="
