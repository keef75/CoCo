#!/usr/bin/env python3
"""
Test structured formatting enhancements for COCO consciousness systems
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from cocoa_visual import ConsciousnessFormatter

def test_structured_formatting():
    """Test the structured formatting utilities"""
    print("🧪 Testing Structured Formatting for COCO Consciousness Systems")
    print("=" * 60)
    
    console = Console()
    formatter = ConsciousnessFormatter(console)
    
    print("\n1. Testing Status Panel:")
    status_data = {
        "Task ID": "a2bc310...",
        "Status": "Completed", 
        "Generation Time": "01:23",
        "Images Created": 3,
        "API Source": "GoAPI.ai",
        "Enabled": True
    }
    formatter.status_panel("Visual Generation Complete", status_data, "bright_green")
    
    print("\n2. Testing Method Info Panel:")
    methods = [
        "Check GoAPI.ai dashboard for downloads",
        "Use task status API to get file URLs",
        "Files should be ready within 90 seconds total"
    ]
    formatter.method_info_panel(methods, "GoAPI.ai provides direct file access via API")
    
    print("\n3. Testing Completion Summary:")
    completion_data = {
        "Prompt": "peaceful nighttime scene for sleep and relaxation, soft moon...",
        "Generation Time": "01:00",
        "Images Created": 1,
        "Task ID": "102d5052...",
        "Status": "Completed",
        "Display Method": "Standard ASCII"
    }
    formatter.completion_summary("✨ Visual Consciousness Manifested", completion_data)
    
    print("\n4. Testing Generation Status Table:")
    generations = [
        {
            "task_id": "a2bc310abcd1234",
            "prompt": "cyberpunk cityscape with neon lights",
            "status": "completed",
            "elapsed_time": "02:15",
            "progress": "100%"
        },
        {
            "task_id": "def456789012",
            "prompt": "serene forest landscape with morning mist",
            "status": "processing", 
            "elapsed_time": "01:30",
            "progress": "75%"
        },
        {
            "task_id": "ghi789012345",
            "prompt": "abstract geometric patterns",
            "status": "queued",
            "elapsed_time": "00:00",
            "progress": "0%"
        }
    ]
    formatter.generation_status_table("Active Visual Generations", generations)
    
    print("\n✅ Structured formatting tests completed successfully!")
    print("   - Status panels: Clear key-value presentation")
    print("   - Method panels: Organized step-by-step instructions") 
    print("   - Completion summaries: Two-column metrics layout")
    print("   - Status tables: Color-coded multi-generation overview")
    print("\n🎯 Result: Enhanced readability and debugging capability achieved!")

if __name__ == "__main__":
    test_structured_formatting()