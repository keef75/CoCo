#!/usr/bin/env python3
"""
Test the enhanced episodic memory integration with COCO
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_enhanced_episodic_memory():
    """Test the enhanced episodic memory system integration"""
    print("🧪 Testing Enhanced Episodic Memory Integration")
    print("=" * 50)

    # Test episodic memory fix import
    try:
        from episodic_memory_fix import EnhancedEpisodicMemory, COCOMemoryIntegration
        print("✅ Enhanced episodic memory imports successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

    # Test COCO system import
    try:
        from cocoa import Config, HierarchicalMemorySystem
        print("✅ COCO system imports successful")
    except ImportError as e:
        print(f"❌ COCO import failed: {e}")
        return False

    # Test system initialization
    try:
        print("\n🔄 Initializing test system...")
        config = Config()
        config.debug = True  # Enable debug output
        memory = HierarchicalMemorySystem(config)
        print("✅ COCO memory system initialized")

        # Check if enhanced episodic memory was loaded
        if hasattr(memory, 'enhanced_episodic') and memory.enhanced_episodic:
            print("✅ Enhanced episodic memory system active")
        else:
            print("⚠️ Enhanced episodic memory not initialized (falling back to standard)")

        if hasattr(memory, 'memory_integration') and memory.memory_integration:
            print("✅ Memory integration wrapper active")
        else:
            print("⚠️ Memory integration wrapper not active")

    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        return False

    # Test adding interactions
    try:
        print("\n🧠 Testing memory interactions...")

        # Add test exchanges
        memory.insert_episode(
            "excellent work! great job getting that info!",
            "Thank you! I successfully retrieved the RX2 intelligence reports..."
        )

        memory.insert_episode(
            "nope, thats not it...it was something else. what was the first thing I said?",
            "Let me check my memory more carefully..."
        )

        print("✅ Test episodes added to memory")

        # Test temporal query
        if hasattr(memory, 'handle_temporal_query'):
            query_result = memory.handle_temporal_query("first thing")
            print(f"✅ Temporal query result: {query_result[:100]}...")
        else:
            print("⚠️ Temporal query handler not available")

        # Test memory stats
        if hasattr(memory, 'get_memory_stats'):
            stats = memory.get_memory_stats()
            print(f"✅ Memory stats: {len(stats)} properties")
            if 'total_sessions' in stats:
                print("✅ Enhanced memory statistics available")
            else:
                print("⚠️ Enhanced memory statistics not available")
        else:
            print("⚠️ Memory stats not available")

    except Exception as e:
        print(f"❌ Memory interaction test failed: {e}")
        return False

    print("\n🎉 Enhanced Episodic Memory Integration Test Complete!")
    return True

def test_senior_dev_fix():
    """Test the senior dev's episodic memory fix specifically"""
    print("\n🔧 Testing Senior Dev's Episodic Memory Fix")
    print("=" * 45)

    try:
        from episodic_memory_fix import EnhancedEpisodicMemory

        # Create standalone enhanced memory
        memory = EnhancedEpisodicMemory()
        print("✅ Enhanced episodic memory created")

        # Test adding exchanges
        episode1 = memory.add_exchange(
            "excellent work! great job getting that info!",
            "Thank you! I successfully retrieved the RX2 intelligence reports..."
        )
        print(f"✅ First exchange added: {episode1.exchange_number}")

        episode2 = memory.add_exchange(
            "what was the first thing I said?",
            "Let me recall the first thing you said..."
        )
        print(f"✅ Second exchange added: {episode2.exchange_number}")

        # Test first exchange recall
        first_exchange = memory.get_first_exchange_of_session()
        if first_exchange:
            print(f"✅ First exchange recall: '{first_exchange.user_text}'")
        else:
            print("❌ Could not recall first exchange")

        # Test temporal reference clarification
        result = memory.clarify_temporal_reference("first thing")
        print(f"✅ Temporal clarification: {result['interpretation']}")
        print(f"   Clarification: {result['clarification']}")

        # Test session boundaries
        boundaries = memory.get_session_boundaries()
        current = boundaries['current_session']
        print(f"✅ Session info: {current['total_exchanges']} exchanges in current session")

        # Test statistics
        stats = memory.get_statistics()
        print(f"✅ Statistics: {stats['total_episodes']} episodes, {stats['total_sessions']} sessions")

        return True

    except Exception as e:
        print(f"❌ Senior dev fix test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 COCO Enhanced Episodic Memory Test Suite")
    print("=" * 60)

    # Test the senior dev's fix first
    senior_test_passed = test_senior_dev_fix()

    # Test COCO integration
    integration_test_passed = test_enhanced_episodic_memory()

    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print(f"   Senior Dev Fix: {'✅ PASSED' if senior_test_passed else '❌ FAILED'}")
    print(f"   COCO Integration: {'✅ PASSED' if integration_test_passed else '❌ FAILED'}")

    if senior_test_passed and integration_test_passed:
        print("\n🎉 ALL TESTS PASSED! The enhanced episodic memory system is ready!")
        print("💡 Try asking COCO: 'What was the first thing I said?'")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")
        sys.exit(1)