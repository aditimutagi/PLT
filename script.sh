#!/bin/bash

# Check if the user has provided a code string to scan
if [ $# -eq 0 ]; then
    echo "Usage: $0 <music_code>"
    echo "Example: $0 'C4 1.0 D4 0.5 chord (C4 D4) 0.75 130 play'"
    exit 1
fi

CODE=$1

python3 scanner.py "$CODE"
