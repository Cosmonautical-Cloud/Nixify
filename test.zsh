#! /bin/zsh

# This script runs the collection's unit tests for the pure-Python
# YAML/Jinja -> Nix conversion logic in plugins/module_utils/nix.py.
python3 -m pytest tests/unit "$@"
