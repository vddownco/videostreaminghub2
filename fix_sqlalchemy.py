#!/usr/bin/env python3
"""
This script patches SQLAlchemy to work with Python 3.13 by fixing
the TypingOnly implementation that's causing compatibility issues.
"""

import os
import sys
import re

try:
    from sqlalchemy.sql.elements import SQLCoreOperations
    sqlalchemy_installed = True
except ImportError:
    sqlalchemy_installed = False
    print("SQLAlchemy not found in the current environment.")
    sys.exit(1)

# Get the path to the elements.py file
import sqlalchemy.sql.elements
elements_path = sqlalchemy.sql.elements.__file__

# Backup the original file
backup_path = elements_path + '.backup'
if not os.path.exists(backup_path):
    print(f"Creating backup of {elements_path} at {backup_path}")
    with open(elements_path, 'r') as f_in:
        with open(backup_path, 'w') as f_out:
            f_out.write(f_in.read())

# Read the file
with open(elements_path, 'r') as f:
    content = f.read()

# Fix the SQLCoreOperations class definition
pattern = r'class SQLCoreOperations\(Generic\[_T_co\], ColumnOperators, TypingOnly\):'
replacement = 'class SQLCoreOperations(Generic[_T_co], ColumnOperators):'

if re.search(pattern, content):
    # Apply the fix
    modified_content = re.sub(pattern, replacement, content)
    
    # Write the modified content back
    with open(elements_path, 'w') as f:
        f.write(modified_content)
    
    print("Successfully patched SQLAlchemy for Python 3.13 compatibility")
else:
    print("Could not find the pattern to replace. SQLAlchemy may have changed.")
    sys.exit(1) 