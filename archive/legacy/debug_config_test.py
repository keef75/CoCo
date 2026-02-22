#!/usr/bin/env python3
"""
Debug test for Config class debug flag
"""

import os

def test_debug_logic():
    """Test the debug logic directly"""

    # Clear environment
    os.environ.pop('COCO_DEBUG', None)
    os.environ.pop('DEBUG', None)

    # Test 1: Both off
    result1 = (os.getenv('COCO_DEBUG', '').lower() in ('true', '1', 'yes') or
               os.getenv('DEBUG', 'false').lower() == 'true')
    print(f"Both off: {result1}")

    # Test 2: COCO_DEBUG on
    os.environ['COCO_DEBUG'] = 'true'
    result2 = (os.getenv('COCO_DEBUG', '').lower() in ('true', '1', 'yes') or
               os.getenv('DEBUG', 'false').lower() == 'true')
    print(f"COCO_DEBUG on: {result2}")

    # Clean up
    os.environ.pop('COCO_DEBUG', None)

    # Test 3: DEBUG on
    os.environ['DEBUG'] = 'true'
    result3 = (os.getenv('COCO_DEBUG', '').lower() in ('true', '1', 'yes') or
               os.getenv('DEBUG', 'false').lower() == 'true')
    print(f"DEBUG on: {result3}")

    # Clean up
    os.environ.pop('DEBUG', None)

if __name__ == "__main__":
    test_debug_logic()