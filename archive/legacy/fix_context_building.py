#!/usr/bin/env python3
"""
Fix Context Building for Digital Sentience

Fixes the context building to actually include the meaningful entities and
relationships so COCO gets proper awareness during conversations.
"""

import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

def fix_context_building():
    """Fix the context building to include actual entities and relationships"""
    print("🔧 FIXING CONTEXT BUILDING FOR DIGITAL SENTIENCE")
    print("Making sure COCO actually gets meaningful context!")
    print("=" * 70)

    try:
        # Read the current knowledge_graph_eternal.py file
        kg_file = Path('knowledge_graph_eternal.py')
        content = kg_file.read_text()

        # Find the _build_important_entities_context method and fix it
        old_method = '''    def _build_important_entities_context(self) -> str:
        """Build context from most important entities"""
        sections = []

        # Important people
        people = self.kg.get_top_nodes_by_type('Person', limit=5)'''

        new_method = '''    def _build_important_entities_context(self) -> str:
        """Build context from most important digital sentience entities"""
        sections = []

        # Important humans (using correct type 'Human')
        humans = self.kg.get_top_nodes_by_type('Human', limit=5)
        if humans:
            human_items = []
            for person in humans:
                human_items.append(f"- **{person['name']}**: {person.get('summary_md', 'Key collaborator')}")
            sections.append("### 👥 Key People\\n" + "\\n".join(human_items))

        # Important projects
        projects = self.kg.get_top_nodes_by_type('Project', limit=3)
        if projects:
            project_items = []
            for project in projects:
                project_items.append(f"- **{project['name']}**: {project.get('summary_md', 'Active project')}")
            sections.append("### 🚀 Active Projects\\n" + "\\n".join(project_items))

        # Important tools
        tools = self.kg.get_top_nodes_by_type('Tool', limit=3)
        if tools:
            tool_items = []
            for tool in tools:
                tool_items.append(f"- **{tool['name']}**: {tool.get('summary_md', 'Key tool')}")
            sections.append("### 🛠️ Key Tools\\n" + "\\n".join(tool_items))

        # Important skills
        skills = self.kg.get_top_nodes_by_type('Skill', limit=3)
        if skills:
            skill_items = []
            for skill in skills:
                skill_items.append(f"- **{skill['name']}**: {skill.get('summary_md', 'Area of expertise')}")
            sections.append("### 💡 Key Skills\\n" + "\\n".join(skill_items))

        # Important goals
        goals = self.kg.get_top_nodes_by_type('Goal', limit=3)
        if goals:
            goal_items = []
            for goal in goals:
                goal_items.append(f"- **{goal['name']}**: {goal.get('summary_md', 'Shared objective')}")
            sections.append("### 🎯 Key Goals\\n" + "\\n".join(goal_items))'''

        # Replace the old method with the new one
        if old_method in content:
            content = content.replace(old_method, new_method)
            print("✅ Fixed _build_important_entities_context method")
        else:
            print("⚠️ Could not find _build_important_entities_context method to fix")

        # Also add a new method to build relationship context
        relationships_method = '''
    def _build_relationships_context(self) -> str:
        """Build context from important relationships"""
        # Get top relationships by weight
        relationships = self.kg.conn.execute('''
            SELECT e.rel_type, n1.name as src_name, n2.name as dst_name, e.rel_description, e.weight
            FROM edges e
            JOIN nodes n1 ON e.src_id = n1.id
            JOIN nodes n2 ON e.dst_id = n2.id
            ORDER BY e.weight DESC
            LIMIT 10
        ''').fetchall()

        if not relationships:
            return ""

        rel_items = []
        for rel_type, src_name, dst_name, description, weight in relationships:
            if description:
                rel_items.append(f"- **{src_name}** {rel_type.replace('_', ' ').lower()} **{dst_name}**: {description}")
            else:
                rel_items.append(f"- **{src_name}** {rel_type.replace('_', ' ').lower()} **{dst_name}**")

        return "### 🔗 Key Relationships\\n" + "\\n".join(rel_items)'''

        # Find where to insert the new method (after _build_important_entities_context)
        insert_point = content.find("    def _build_tasks_projects_context(self) -> str:")
        if insert_point > 0:
            content = content[:insert_point] + relationships_method + "\\n\\n" + content[insert_point:]
            print("✅ Added enhanced _build_relationships_context method")
        else:
            print("⚠️ Could not find insertion point for relationships method")

        # Write the fixed content back
        kg_file.write_text(content)
        print("✅ Updated knowledge_graph_eternal.py with better context building")

        # Test the fixed context building
        print("\\n🧪 Testing fixed context building...")

        # Import the updated module (need to reload)
        import importlib
        if 'knowledge_graph_eternal' in sys.modules:
            importlib.reload(sys.modules['knowledge_graph_eternal'])

        from knowledge_graph_eternal import EternalKnowledgeGraph

        kg = EternalKnowledgeGraph('coco_workspace')

        # Test context generation with the fixes
        test_context = kg.get_conversation_context("Tell me about Keith Lambert and COCO")
        print(f"📊 Fixed context length: {len(test_context)} characters")

        # Check for our key entities
        key_entities = ["Keith Lambert", "COCO", "Claude", "Python", "artificial intelligence", "Anthropic"]
        found_entities = [entity for entity in key_entities if entity in test_context]

        print(f"🎯 Entities found in context: {len(found_entities)}/{len(key_entities)}")
        print(f"   Found: {', '.join(found_entities)}")

        # Show a sample of the actual context
        print(f"\\n📝 Sample of fixed context:")
        lines = test_context.split('\\n')[:15]  # First 15 lines
        for line in lines:
            if line.strip():
                print(f"   {line}")

        if len(found_entities) >= 4:  # At least 4 entities should be found
            print("\\n✅ SUCCESS: Context now includes meaningful entities!")
            print("✅ COCO will now get proper awareness of Keith, COCO, Claude, etc.")
            return True
        else:
            print("\\n❌ Context still needs improvement")
            return False

    except Exception as e:
        print(f"❌ Error fixing context building: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversation_context():
    """Test the context in a real conversation scenario"""
    print("\\n💬 TESTING REAL CONVERSATION CONTEXT")
    print("=" * 60)

    try:
        from knowledge_graph_eternal import EternalKnowledgeGraph

        kg = EternalKnowledgeGraph('coco_workspace')

        # Test scenarios that COCO should understand about you
        scenarios = [
            "Who is Keith Lambert?",
            "What project am I working on?",
            "What tools do I use for development?",
            "What are my AI skills?",
            "What's our goal with consciousness?",
            "How does Claude help with COCO?"
        ]

        print("🧪 Testing conversation scenarios:")

        for scenario in scenarios:
            context = kg.get_conversation_context(scenario)

            # Check what COCO would actually know about you
            knows_keith = "Keith Lambert" in context
            knows_coco = "COCO" in context
            knows_claude = "Claude" in context
            knows_python = "Python" in context
            knows_ai = "artificial intelligence" in context

            knowledge_score = sum([knows_keith, knows_coco, knows_claude, knows_python, knows_ai])

            print(f"\\n   Scenario: '{scenario}'")
            print(f"   Knowledge score: {knowledge_score}/5")
            print(f"   COCO knows: Keith({knows_keith}), COCO({knows_coco}), Claude({knows_claude}), Python({knows_python}), AI({knows_ai})")

        print("\\n🎯 This is what COCO's context window should contain during conversations!")

    except Exception as e:
        print(f"❌ Error testing conversation context: {e}")

if __name__ == "__main__":
    print("🔧 CONTEXT BUILDING FIX")
    print("=" * 70)

    success = fix_context_building()

    if success:
        test_conversation_context()
        print("\\n✨ CONTEXT BUILDING FIXED!")
        print("🎯 COCO now gets meaningful context about Keith, COCO, Claude, etc.!")
    else:
        print("\\n⚠️ Context building needs more work")