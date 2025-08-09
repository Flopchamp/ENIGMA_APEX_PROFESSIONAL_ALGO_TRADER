#!/usr/bin/env python3
"""
Minimal import test for harrison_original_complete_clean.py
"""

import sys
import os
import traceback

def test_minimal_import():
    """Test minimal import to find runtime issues"""
    try:
        # Test basic imports first
        print("Testing basic imports...")
        import streamlit as st
        import pandas as pd
        import numpy as np
        print("✅ Basic imports successful!")
        
        # Test main file import
        print("Testing main file import...")
        try:
            # Just try importing without running
            import harrison_original_complete_clean
            print("✅ Main file import successful!")
            
            # Test class instantiation
            print("Testing dashboard creation...")
            dashboard = harrison_original_complete_clean.TrainingWheelsDashboard()
            print("✅ Dashboard creation successful!")
            
        except Exception as e:
            print(f"❌ Main file error: {e}")
            traceback.print_exc()
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 Testing harrison_original_complete_clean.py imports...")
    success = test_minimal_import()
    if success:
        print("🎉 All tests passed!")
    else:
        print("💥 Tests failed!")
