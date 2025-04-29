#%%
# This program should read the target folder and look for all the files with a certain pattern. Then
# it should dump the file list in the corresponding json file.
import sys
try:
    target_folder = sys.argv[1]
    pattern = sys.argv[2]
except IndexError:
    print("Usage: python fill_json.py <target_folder> <pattern>")
    print("Example: python fill_json.py ../fluka_run *.99")
    sys.exit(1)

# Read json file
json_path = "./inputfile.json"

import json

with open(json_path, 'r') as f:
    json_data = json.load(f)

# Search for all the files in the target folder that starts end with the pattern
# and start with the prefix given by the json file
import glob
import os

file_list = glob.glob(os.path.join(target_folder, pattern))

# For each file in the list, check if the basename starts with the prefix
# and add it to the json inputs
for name, options in json_data.items():
   prefix = options["prefix"]
   for file in file_list:
      basename = os.path.basename(file)
      if basename.startswith(prefix):
            options["inputs"].append(file)

# Write the json file "inputfile_filled.json"
with open("inputfile_filled.json", 'w') as f:
    json.dump(json_data, f, indent=4)