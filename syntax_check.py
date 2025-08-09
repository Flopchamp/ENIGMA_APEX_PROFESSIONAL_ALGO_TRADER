#!/usr/bin/env python3
"""
Syntax validation test for harrison_original_complete_clean.py
"""

import sys
import ast
import traceback

def validate_python_syntax(filename):
    """Validate Python syntax of a file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Try to parse the AST
        ast.parse(source_code)
        print(f"✅ {filename} has valid Python syntax!")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax Error in {filename}:")
        print(f"   Line {e.lineno}: {e.text.strip() if e.text else 'N/A'}")
        print(f"   Error: {e.msg}")
        print(f"   Position: {' ' * (e.offset - 1 if e.offset else 0)}^")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error validating {filename}: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    filename = r"c:\Users\alooh\OneDrive\Pictures\ENIGMA_APEX_PROFESSIONAL_CLIENT_PACKAGE\harrison_original_complete_clean.py"
    validate_python_syntax(filename)
