#!/bin/bash

# Usage: ./run.sh tests/data/prose or foofah

folder_path="$1"  # Get the first command-line argument

if [ -d "$folder_path" ]; then
    # Traverse all file names in the folder and print them
    for file_name in "$folder_path"/*; do
        base_name=$(basename "$file_name")
        if [ "$base_name" != '.DS_Store' ]; then
            echo "------------------------"
            echo "experiment progress: ${file_name}"
            echo "------------------------"
            # Run the Python script
            python foofah.py --input "${file_name}"
        fi
    done
else
    echo "Folder does not exist: $folder_path"
    exit 1
fi
