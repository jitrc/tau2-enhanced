#!/bin/bash
# Regenerate all analysis reports from enhanced log files

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔄 Regenerating all analysis reports..."
echo ""

# Explicit mapping of input log files to output directories
# Format: python3 analyze_simple_logs.py <input_log> -o <output_dir>

echo "[1/5] Processing: airline_gemini2_5_flash_10tasks_2t_enhanced_logs.json"
python3 "$SCRIPT_DIR/analyze_simple_logs.py" \
    "$PROJECT_ROOT/samples/logs/airline_gemini2_5_flash_10tasks_2t_enhanced_logs.json" \
    -o "$PROJECT_ROOT/samples/analysis/airline_gemini2_5_flash_10tasks_llm_agent"
echo "  ✅ Complete: samples/analysis/airline_gemini2_5_flash_10tasks_llm_agent/"
echo ""

echo "[2/5] Processing: airline_gemini2_5_flash_10tasks_2t_context_agent_enhanced_logs.json"
python3 "$SCRIPT_DIR/analyze_simple_logs.py" \
    "$PROJECT_ROOT/samples/logs/airline_gemini2_5_flash_10tasks_2t_context_agent_enhanced_logs.json" \
    -o "$PROJECT_ROOT/samples/analysis/airline_gemini2_5_flash_10tasks_context_agent"
echo "  ✅ Complete: samples/analysis/airline_gemini2_5_flash_10tasks_context_agent/"
echo ""

echo "[3/5] Processing: airline_gemini2_5_flash_10tasks_2t_enhanced_agent_enhanced_logs.json"
python3 "$SCRIPT_DIR/analyze_simple_logs.py" \
    "$PROJECT_ROOT/samples/logs/airline_gemini2_5_flash_10tasks_2t_enhanced_agent_enhanced_logs.json" \
    -o "$PROJECT_ROOT/samples/analysis/airline_gemini2_5_flash_10tasks_enhanced_agent"
echo "  ✅ Complete: samples/analysis/airline_gemini2_5_flash_10tasks_enhanced_agent/"
echo ""

echo "[4/5] Processing: airline_gemini2_5_flash_10tasks_2t_retry_agent_enhanced_logs.json"
python3 "$SCRIPT_DIR/analyze_simple_logs.py" \
    "$PROJECT_ROOT/samples/logs/airline_gemini2_5_flash_10tasks_2t_retry_agent_enhanced_logs.json" \
    -o "$PROJECT_ROOT/samples/analysis/airline_gemini2_5_flash_10tasks_retry_agent"
echo "  ✅ Complete: samples/analysis/airline_gemini2_5_flash_10tasks_retry_agent/"
echo ""

echo "[5/5] Processing: baseline_airline_xai_grok3_gemini2_5_flash_reduced.json"
python3 "$SCRIPT_DIR/analyze_simple_logs.py" \
    "$PROJECT_ROOT/samples/logs/baseline_airline_xai_grok3_gemini2_5_flash_reduced.json" \
    -o "$PROJECT_ROOT/samples/analysis/baseline_airline_xai_grok3_gemini2_5_flash"
echo "  ✅ Complete: samples/analysis/baseline_airline_xai_grok3_gemini2_5_flash/"
echo ""

echo "🎉 All analysis reports regenerated successfully!"
echo ""
echo "📁 Reports are available in: $PROJECT_ROOT/samples/analysis/"
