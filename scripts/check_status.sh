#!/bin/bash
# Quick status check script

echo "=================================="
echo "DATA RETRIEVAL STATUS"
echo "=================================="
echo ""
echo "Output Directory:"
du -sh output/ 2>/dev/null || echo "Not created yet"
echo ""
echo "Files Created:"
ls -1 output/*.jsonl 2>/dev/null | wc -l
echo ""
echo "Total Records Retrieved:"
total=0
if ls output/*.jsonl 1> /dev/null 2>&1; then
    for f in output/*.jsonl; do
        count=$(wc -l < "$f" 2>/dev/null || echo 0)
        total=$((total + count))
    done
fi
echo "$total records"
echo ""
echo "Progress:"
if [ $total -gt 0 ]; then
    progress=$(echo "scale=2; $total / 21179498 * 100" | bc)
    echo "${progress}% complete"
fi
echo ""
echo "=================================="

# Made with Bob
