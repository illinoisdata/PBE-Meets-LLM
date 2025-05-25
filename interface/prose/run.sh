#!/bin/bash

folder_path="$1"  # Get the first command-line argument

if [ -d "$folder_path" ]; then
    # Traverse all files in the folder
    for file_path in "$folder_path"/*.json; do
        base_name=$(basename "$file_path")  # e.g., file.json
        name_without_ext="${base_name%.*}"  # e.g., file

        # Skip macOS system file
        if [ "$base_name" != ".DS_Store" ]; then
            echo "------------------------"
            echo "experiment progress: ${file_path}"
            echo "------------------------"
            # Run the .NET app with full path and file name
            dotnet run "$file_path" "$name_without_ext"
        fi
    done
else
    echo "Folder does not exist: $folder_path"
    exit 1
fi

