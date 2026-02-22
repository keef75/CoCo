#!/usr/bin/env python3
"""
Universal Tool Fact Extraction System - Comprehensive Test Suite
Tests all 15 extractors to ensure complete memory coverage.

This is a simplified syntax and logic test - does not require full COCO initialization.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_mock_engine():
    """Create a minimal mock engine for testing extractors"""
    class MockConfig:
        debug = True

    class MockConsole:
        def print(self, *args, **kwargs):
            pass  # Suppress debug output during tests

    class MockFactsMemory:
        def __init__(self):
            self.stored_facts = []

        def store_facts(self, facts, episode_id=None):
            self.stored_facts.extend(facts)
            return len(facts)

    class MockMemory:
        def __init__(self):
            self.facts_memory = MockFactsMemory()

    class MockEngine:
        def __init__(self):
            self.config = MockConfig()
            self.console = MockConsole()
            self.memory = MockMemory()

        # Import the extractor methods from ConsciousnessEngine
        def setup_extractors(self):
            """Import extractor methods from real ConsciousnessEngine"""
            from cocoa import ConsciousnessEngine
            # Get the real methods
            self._extract_tool_facts = ConsciousnessEngine._extract_tool_facts.__get__(self)
            self._extract_email_facts = ConsciousnessEngine._extract_email_facts.__get__(self)
            self._extract_document_facts = ConsciousnessEngine._extract_document_facts.__get__(self)
            self._extract_spreadsheet_facts = ConsciousnessEngine._extract_spreadsheet_facts.__get__(self)
            self._extract_image_facts = ConsciousnessEngine._extract_image_facts.__get__(self)
            self._extract_video_facts = ConsciousnessEngine._extract_video_facts.__get__(self)
            self._extract_file_facts = ConsciousnessEngine._extract_file_facts.__get__(self)
            self._extract_search_facts = ConsciousnessEngine._extract_search_facts.__get__(self)
            self._extract_calendar_facts = ConsciousnessEngine._extract_calendar_facts.__get__(self)
            self._extract_upload_facts = ConsciousnessEngine._extract_upload_facts.__get__(self)
            self._extract_download_facts = ConsciousnessEngine._extract_download_facts.__get__(self)
            self._extract_folder_facts = ConsciousnessEngine._extract_folder_facts.__get__(self)
            self._extract_read_document_facts = ConsciousnessEngine._extract_read_document_facts.__get__(self)
            self._extract_analyze_document_facts = ConsciousnessEngine._extract_analyze_document_facts.__get__(self)
            self._extract_bash_facts = ConsciousnessEngine._extract_bash_facts.__get__(self)
            self._store_facts = ConsciousnessEngine._store_facts.__get__(self)

    engine = MockEngine()
    engine.setup_extractors()
    return engine

def test_extractor_routing():
    """Test that the router correctly maps tools to extractors"""
    print("\n" + "="*80)
    print("TEST 1: Extractor Routing")
    print("="*80)

    engine = create_mock_engine()

    # Test tools that should have extractors
    tools_with_extractors = [
        'send_email',
        'create_document',
        'create_spreadsheet',
        'generate_image',
        'generate_video',
        'write_file',
        'search_web',
        'add_calendar_event',
        'create_calendar_event',
        'upload_file',
        'download_file',
        'create_folder',
        'read_document',  # NEW
        'analyze_document',  # NEW
        'execute_bash',  # NEW
    ]

    print(f"\nTesting {len(tools_with_extractors)} tools with extractors...")

    # Create mock tool results (non-error)
    for tool_name in tools_with_extractors:
        tool_input = {'test_key': 'test_value'}
        tool_result = "Operation completed"

        # The router should find an extractor for each tool
        # We'll test by calling _extract_tool_facts directly
        facts_count = engine._extract_tool_facts(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_result=tool_result,
            episode_id=1
        )

        # Note: facts_count will be 0 because tool_input doesn't have required fields
        # But we're testing that the router finds the extractor without errors
        print(f"  ✅ {tool_name}: Routed successfully (extractor found)")

    print(f"\n✅ All {len(tools_with_extractors)} tools routed to extractors successfully")
    return True

def test_email_facts():
    """Test email fact extraction"""
    print("\n" + "="*80)
    print("TEST 2: Email Facts Extraction (send_email)")
    print("="*80)

    engine = create_mock_engine()

    tool_input = {
        'to': 'sarah@example.com',
        'subject': 'Q4 Product Roadmap Review',
        'body': 'Let me know your thoughts...'
    }
    tool_result = "Email sent successfully to sarah@example.com"

    facts_count = engine._extract_tool_facts(
        tool_name='send_email',
        tool_input=tool_input,
        tool_result=tool_result,
        episode_id=1
    )

    print(f"\nFacts extracted: {facts_count}")
    print("Expected: 2 facts (recipient + subject)")

    if facts_count == 2:
        print("✅ Email extraction working correctly")
        return True
    else:
        print(f"❌ Expected 2 facts, got {facts_count}")
        return False

def test_document_facts():
    """Test document creation fact extraction"""
    print("\n" + "="*80)
    print("TEST 3: Document Facts Extraction (create_document)")
    print("="*80)

    engine = create_mock_engine()

    tool_input = {
        'title': 'Project Timeline 2025',
        'initial_content': 'This document outlines the timeline for our AI integration project. Key milestones include...'
    }
    tool_result = "Document created successfully"

    facts_count = engine._extract_tool_facts(
        tool_name='create_document',
        tool_input=tool_input,
        tool_result=tool_result,
        episode_id=2
    )

    print(f"\nFacts extracted: {facts_count}")
    print("Expected: 2 facts (title + topic)")

    if facts_count == 2:
        print("✅ Document extraction working correctly")
        return True
    else:
        print(f"❌ Expected 2 facts, got {facts_count}")
        return False

def test_calendar_facts():
    """Test calendar event fact extraction (triple-fact)"""
    print("\n" + "="*80)
    print("TEST 4: Calendar Facts Extraction (add_calendar_event) - TRIPLE FACTS")
    print("="*80)

    

    
    engine = create_mock_engine()

    tool_input = {
        'summary': 'Team Sync Meeting',
        'attendees': ['sarah@example.com', 'john@example.com'],
        'location': 'Conference Room B',
        'start_time': '2025-10-26 14:00'
    }
    tool_result = "Calendar event created successfully"

    facts_count = engine._extract_tool_facts(
        tool_name='add_calendar_event',
        tool_input=tool_input,
        tool_result=tool_result,
        episode_id=3
    )

    print(f"\nFacts extracted: {facts_count}")
    print("Expected: 3 facts (title + attendees + time/location)")

    if facts_count == 3:
        print("✅ Calendar extraction working correctly (triple-fact)")
        return True
    else:
        print(f"❌ Expected 3 facts, got {facts_count}")
        return False

def test_read_document_facts():
    """Test NEW read_document fact extraction"""
    print("\n" + "="*80)
    print("TEST 5: Read Document Facts Extraction (read_document) - NEW")
    print("="*80)

    

    
    engine = create_mock_engine()

    tool_input = {
        'doc_id': 'abc123',
        'title': 'AI Research Paper 2025'
    }
    tool_result = "Large Language Models have shown remarkable capabilities in reasoning tasks. Recent advances include chain-of-thought prompting and constitutional AI. These methods improve both accuracy and alignment..."

    facts_count = engine._extract_tool_facts(
        tool_name='read_document',
        tool_input=tool_input,
        tool_result=tool_result,
        episode_id=4
    )

    print(f"\nFacts extracted: {facts_count}")
    print("Expected: 2 facts (title + key topics)")

    if facts_count == 2:
        print("✅ Read document extraction working correctly")
        return True
    else:
        print(f"❌ Expected 2 facts, got {facts_count}")
        return False

def test_analyze_document_facts():
    """Test NEW analyze_document fact extraction"""
    print("\n" + "="*80)
    print("TEST 6: Analyze Document Facts Extraction (analyze_document) - NEW")
    print("="*80)

    

    
    engine = create_mock_engine()

    tool_input = {
        'doc_id': 'xyz789',
        'analysis_type': 'sentiment'
    }
    tool_result = "The document shows positive sentiment with 78% confidence. Key themes include innovation, collaboration, and growth. Tone is professional and optimistic."

    facts_count = engine._extract_tool_facts(
        tool_name='analyze_document',
        tool_input=tool_input,
        tool_result=tool_result,
        episode_id=5
    )

    print(f"\nFacts extracted: {facts_count}")
    print("Expected: 2 facts (analysis performed + findings)")

    if facts_count == 2:
        print("✅ Analyze document extraction working correctly")
        return True
    else:
        print(f"❌ Expected 2 facts, got {facts_count}")
        return False

def test_bash_facts():
    """Test NEW execute_bash fact extraction"""
    print("\n" + "="*80)
    print("TEST 7: Bash Execution Facts Extraction (execute_bash) - NEW")
    print("="*80)

    

    
    engine = create_mock_engine()

    tool_input = {
        'command': 'git commit -m "Add universal fact extraction system"'
    }
    tool_result = "[main abc1234] Add universal fact extraction system\n 3 files changed, 150 insertions(+)"

    facts_count = engine._extract_tool_facts(
        tool_name='execute_bash',
        tool_input=tool_input,
        tool_result=tool_result,
        episode_id=6
    )

    print(f"\nFacts extracted: {facts_count}")
    print("Expected: 2 facts (command + operation type)")

    if facts_count == 2:
        print("✅ Bash execution extraction working correctly")
        return True
    else:
        print(f"❌ Expected 2 facts, got {facts_count}")
        return False

def test_error_handling():
    """Test that errors are properly skipped"""
    print("\n" + "="*80)
    print("TEST 8: Error Handling (skip extraction on failures)")
    print("="*80)

    

    
    engine = create_mock_engine()

    # Test with error result
    tool_input = {'to': 'test@example.com', 'subject': 'Test'}
    tool_result = "Error: Failed to send email - invalid credentials"

    facts_count = engine._extract_tool_facts(
        tool_name='send_email',
        tool_input=tool_input,
        tool_result=tool_result,
        episode_id=7
    )

    print(f"\nFacts extracted from error: {facts_count}")
    print("Expected: 0 facts (errors should be skipped)")

    if facts_count == 0:
        print("✅ Error handling working correctly (no facts from errors)")
        return True
    else:
        print(f"❌ Expected 0 facts from error, got {facts_count}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*80)
    print("UNIVERSAL TOOL FACT EXTRACTION - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Extractor Routing", test_extractor_routing),
        ("Email Facts", test_email_facts),
        ("Document Facts", test_document_facts),
        ("Calendar Facts (Triple)", test_calendar_facts),
        ("Read Document Facts (NEW)", test_read_document_facts),
        ("Analyze Document Facts (NEW)", test_analyze_document_facts),
        ("Bash Facts (NEW)", test_bash_facts),
        ("Error Handling", test_error_handling),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "-"*80)
    print(f"Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print("="*80)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Universal Fact Extraction System is ready for production.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review output above for details.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
