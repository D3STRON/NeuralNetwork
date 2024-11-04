#!/bin/bash

# Run pre-commit hooks, including poetry-gen-init and black
pre-commit run --all-files

# Add any new __init__.py files generated by poetry-gen-init
git add .

# Commit the new files if there are any changes
if ! git diff --cached --quiet; then
    git commit -m "Auto-commit generated __init__.py files"
fi
