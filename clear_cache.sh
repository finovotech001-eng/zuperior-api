#!/bin/bash
echo "Clearing Python cache..."
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
echo "✓ Cache cleared!"
echo ""
echo "The Transaction model now uses 'metadata_json' instead of 'metadata'"
echo "Please restart your server now."
