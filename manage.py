#!/usr/bin/env python
"""
Wrapper script to run Django management commands from the root directory.
Automatically changes to the backend directory and delegates to the real manage.py
"""
import os
import sys

if __name__ == "__main__":
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    sys.path.insert(0, backend_dir)
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shand.settings')
    
    # Import Django's execute_from_command_line
    from django.core.management import execute_from_command_line
    
    sys.exit(execute_from_command_line(sys.argv))
