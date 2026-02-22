#!/usr/bin/env python3
"""
Test script to verify the dual-axis memory JSON parsing fix
"""

import json
import sqlite3
import tempfile
import os
from datetime import datetime
from pathlib import Path

# Add current directory to path so we can import cocoa
import sys
sys.path.insert(0, '.')

from cocoa import Config, DualAxisMemory

def test_json_parsing_fix():
    """Test that the JSON parsing issue is resolved"""
    print("🧪 Testing dual-axis memory JSON parsing fix...")

    # Create temporary workspace
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup temporary config
        config = Config()
        config.workspace = temp_dir
        config.debug = True

        # Enable dual axis memory
        os.environ['DUAL_AXIS_MEMORY_ENABLED'] = 'true'
        os.environ['PARALLEL_TRACKS_ENABLED'] = 'true'
        os.environ['MEMORY_METADATA_ENRICHMENT'] = 'true'

        try:
            # Initialize dual axis memory system
            print("📋 Initializing dual-axis memory system...")
            dual_memory = DualAxisMemory(config)

            # Create problematic database entries to test fix
            print("🔧 Creating test database entries with potential JSON issues...")

            # Insert a narrative thread with empty/problematic JSON fields
            dual_memory.db.execute("""
                INSERT INTO narrative_threads (
                    thread_id, thread_name, started_date, last_updated, thread_type,
                    status, episode_ids, key_moments, summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "test_thread_1", "Test Thread", datetime.now().isoformat(),
                datetime.now().isoformat(), 'topic', 'active',
                "", "",  # Empty strings that would cause JSON parsing errors
                "Test thread"
            ))

            # Insert another with whitespace-only JSON fields
            dual_memory.db.execute("""
                INSERT INTO narrative_threads (
                    thread_id, thread_name, started_date, last_updated, thread_type,
                    status, episode_ids, key_moments, summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "test_thread_2", "Test Thread 2", datetime.now().isoformat(),
                datetime.now().isoformat(), 'topic', 'active',
                "   ", "\t\n",  # Whitespace-only strings that would cause JSON parsing errors
                "Test thread 2"
            ))

            dual_memory.db.commit()

            # Test storing enriched episodes (this was failing before the fix)
            print("📝 Testing episode storage with potentially problematic existing data...")

            session_id = "test_session_123"
            user_text = "Test user message that mentions various topics"
            agent_text = "Test agent response that continues the conversation"
            exchange_context = []

            # This should not fail with JSON parsing errors anymore
            episode_id = dual_memory.store_enriched_episode(
                session_id, user_text, agent_text, exchange_context
            )

            if episode_id:
                print(f"✅ Successfully stored episode: {episode_id}")
                print("✅ JSON parsing fix is working!")

                # Test another episode to make sure the thread updates work
                episode_id_2 = dual_memory.store_enriched_episode(
                    session_id,
                    "Follow-up message about the same topic",
                    "Agent follows up on the topic discussion",
                    exchange_context + [{'user': user_text, 'agent': agent_text}]
                )

                if episode_id_2:
                    print(f"✅ Successfully stored second episode: {episode_id_2}")
                    print("✅ Narrative thread updates working correctly!")
                else:
                    print("❌ Second episode failed to store")
                    return False
            else:
                print("❌ Episode storage failed - JSON parsing issue may still exist")
                return False

            # Test querying the data
            print("🔍 Testing data retrieval...")
            cursor = dual_memory.db.execute("SELECT * FROM episodic_timeline ORDER BY timestamp DESC LIMIT 2")
            episodes = cursor.fetchall()

            print(f"📊 Retrieved {len(episodes)} episodes from timeline")
            for i, episode in enumerate(episodes, 1):
                print(f"   Episode {i}: {episode[0]} - {episode[12][:50]}...")  # episode_id and user_input preview

            # Test narrative threads
            cursor = dual_memory.db.execute("SELECT thread_id, episode_ids, key_moments FROM narrative_threads")
            threads = cursor.fetchall()

            print(f"📋 Found {len(threads)} narrative threads")
            for thread in threads:
                thread_id, episode_ids_json, key_moments_json = thread
                try:
                    # This should not fail anymore
                    episode_ids = json.loads(episode_ids_json) if episode_ids_json and episode_ids_json.strip() else []
                    key_moments = json.loads(key_moments_json) if key_moments_json and key_moments_json.strip() else []
                    print(f"   Thread {thread_id}: {len(episode_ids)} episodes, {len(key_moments)} key moments")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing still failing for thread {thread_id}: {e}")
                    return False

            print("🎉 All tests passed! Dual-axis memory JSON parsing fix is working correctly.")
            return True

        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_json_parsing_fix()
    if success:
        print("\n✅ DUAL-AXIS MEMORY FIX VERIFIED!")
        print("The JSON parsing issue in the narrative threads system has been resolved.")
        print("COCO should now store episodes without 'Failed to store enriched episode' errors.")
    else:
        print("\n❌ FIX VERIFICATION FAILED!")
        print("There may still be JSON parsing issues in the dual-axis memory system.")

    # Cleanup environment variables
    for var in ['DUAL_AXIS_MEMORY_ENABLED', 'PARALLEL_TRACKS_ENABLED', 'MEMORY_METADATA_ENRICHMENT']:
        if var in os.environ:
            del os.environ[var]