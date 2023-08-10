#!/bin/bash

# Create a new file
touch gpt-input.md

# Add initial sentence
echo "These are files of a python project:" >> gpt-input.md

# Read .gptignore and convert patterns to regex
ignore_patterns=$(cat .gptignore | sed 's/./\./g' | sed 's/*/.*/g' | sed 's///\//g')

# Go through folders and add the content of .py files
find . -name "*.py" -type f | while read file
do
    # Check if file matches any ignore pattern
    if ! echo "$file" | grep -q -E "$ignore_patterns"; then
        echo -e "\n`$file`:\n```" >> gpt-input.md
        cat "$file" >> gpt-input.md
        echo -e "```" >> gpt-input.md
    fi
done