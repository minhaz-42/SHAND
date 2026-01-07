#!/bin/bash

# SHAND Development Server Launcher
# Run from project root to start Django development server

cd "$(dirname "$0")/backend"
python3 manage.py runserver
