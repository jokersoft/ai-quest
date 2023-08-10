import os
import fnmatch

# Create a new file
with open('gpt-input.md', 'w') as f:
    f.write("These are files of a python project:\n")

# Read .gptignore and store patterns
with open('.gptignore', 'r') as f:
    ignore_patterns = f.read().splitlines()

# Go through folders and add the content of .py files
for root, dirnames, filenames in os.walk('.'):
    for filename in fnmatch.filter(filenames, '*.py'):
        file_path = os.path.join(root, filename)
        # Check if file matches any ignore pattern
        if not any(fnmatch.fnmatch(file_path, pattern) for pattern in ignore_patterns):
            with open('gpt-input.md', 'a') as f:
                f.write("\n`{}`:\n```\n".format(file_path))
                with open(file_path, 'r') as py_file:
                    f.write(py_file.read())
                f.write("\n")
