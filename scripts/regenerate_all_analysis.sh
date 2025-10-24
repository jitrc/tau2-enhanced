#!/bin/bash
# Regenerate all analysis reports from enhanced log files
# Usage: ./regenerate_all_analysis.sh [item_number]
#   item_number: Optional. Specify which item to process (1-6). If omitted, all items are processed.

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration: Array of input log file and output directory pairs
# Format: "input_log_name:output_dir_name"
declare -a ANALYSES=(
    "baseline_airline_xai_grok3_gemini2_5_flash_reduced.json:baseline_airline_xai_grok3_gemini2_5_flash"
    "baseline_airline_gemini2_5_flash_reduced.json:baseline_airline_gemini2_5_flash"
    "airline_gemini2_5_flash_10tasks_2t_enhanced_logs.json:airline_gemini2_5_flash_10tasks_llm_agent"
    "airline_gemini2_5_flash_10tasks_2t_context_agent_enhanced_logs.json:airline_gemini2_5_flash_10tasks_context_agent"
    "airline_gemini2_5_flash_10tasks_2t_enhanced_agent_enhanced_logs.json:airline_gemini2_5_flash_10tasks_enhanced_agent"
    "airline_gemini2_5_flash_10tasks_2t_retry_agent_enhanced_logs.json:airline_gemini2_5_flash_10tasks_retry_agent"
)

# Parse optional argument
ITEM_NUMBER="$1"
TOTAL=${#ANALYSES[@]}

if [ -n "$ITEM_NUMBER" ]; then
    # Validate item number
    if ! [[ "$ITEM_NUMBER" =~ ^[0-9]+$ ]] || [ "$ITEM_NUMBER" -lt 1 ] || [ "$ITEM_NUMBER" -gt "$TOTAL" ]; then
        echo "❌ Error: Item number must be between 1 and $TOTAL"
        echo "Usage: $0 [item_number]"
        exit 1
    fi
    echo "🔄 Regenerating analysis report for item #$ITEM_NUMBER..."
else
    echo "🔄 Regenerating all analysis reports..."
fi
echo ""

COUNT=0

for entry in "${ANALYSES[@]}"; do
    COUNT=$((COUNT + 1))

    # Skip if a specific item was requested and this isn't it
    if [ -n "$ITEM_NUMBER" ] && [ "$COUNT" -ne "$ITEM_NUMBER" ]; then
        continue
    fi

    # Split entry into input and output
    IFS=':' read -r INPUT_LOG OUTPUT_DIR <<< "$entry"

    INPUT_PATH="$PROJECT_ROOT/samples/logs/$INPUT_LOG"
    OUTPUT_PATH="$PROJECT_ROOT/samples/analysis/$OUTPUT_DIR"

    echo "[$COUNT/$TOTAL] Processing: $INPUT_LOG"

    # Print the command that will be executed
    CMD="python3 \"$SCRIPT_DIR/analyze_simple_logs.py\" \"$INPUT_PATH\" -o \"$OUTPUT_PATH\""
    echo "  🔧 Command: $CMD"

    # Execute the command
    python3 "$SCRIPT_DIR/analyze_simple_logs.py" "$INPUT_PATH" -o "$OUTPUT_PATH"

    echo "  ✅ Complete: samples/analysis/$OUTPUT_DIR/"
    echo ""
done

echo "🎉 All analysis reports regenerated successfully!"
echo ""
echo "📁 Reports are available in: $PROJECT_ROOT/samples/analysis/"
