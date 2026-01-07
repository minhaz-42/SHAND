#!/bin/bash

# SHAND Django Management Script
# Usage: ./manage.sh <command> [args...]
# Examples:
#   ./manage.sh runserver
#   ./manage.sh migrate
#   ./manage.sh test

cd "$(dirname "$0")/backend"
python3 manage.py "$@"
