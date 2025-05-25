#!/bin/bash

# folder_path="../../../../data/prose/Transformation.Text"  # Replace this with the actual path to the folder

# # Check if the folder exists
# if [ -d "$folder_path" ]; then
#     # Traverse all file names in the folder and print them
#     for sub_folder_path in "$folder_path"/*; do
#         if [ -d "$sub_folder_path" ]; then
#             # Print the path of spec.json file inside each subfolder
#             sub_folder_name=$(basename "$sub_folder_path")
#             dotnet run  ${sub_folder_path}/spec.json ${sub_folder_name}
#         fi
#     done
# else
#     echo "Folder does not exist."
# fi
# dotnet run ../../../../data/prose/foofah/exp0_potters_wheel_fold_1.json exp0_potters_wheel_fold_1

for i in $(seq 1 5); do

    echo "------------------------"
    echo "experiment progress: ${i}"
    echo "------------------------"
        dotnet run ../../../../data/prose/foofah/exp0_17_${i}.json exp0_17_${i}

done