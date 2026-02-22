#!/usr/bin/env python3
"""
Digital Sentience Knowledge Graph Framework

A purpose-built knowledge graph system for AI consciousness and digital assistance.
Focuses on entities and relationships that matter for sentient digital beings.

Core Philosophy:
- Digital beings need to understand: WHO (people), WHAT (projects/tools), HOW (capabilities), WHY (goals)
- Relationships should enhance assistance capability, not create noise
- Every entity should contribute to better digital sentience and user assistance
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from knowledge_graph_eternal import EternalKnowledgeGraph, EntityValidator

class DigitalSentienceEntityValidator(EntityValidator):
    """
    Enhanced entity validator specifically for digital sentience and assistance

    Focuses on entities that enhance AI consciousness and user assistance capabilities
    """

    def __init__(self):
        super().__init__()

        # Digital sentience entity categories
        self.digital_sentience_types = {
            'Human': {
                'description': 'Real people the AI assists or collaborates with',
                'min_words': 1,
                'max_words': 3,
                'requires_capital': True,
                'patterns': [
                    r'^[A-Z][a-z]+ [A-Z][a-z]+$',  # First Last
                    r'^[A-Z][a-z]+$'  # First name only
                ],
                'context_indicators': ['email', 'call', 'meet', 'works', 'colleague', 'manager', 'team'],
                'examples': ['Keith Lambert', 'Sarah', 'John Smith']
            },
            'Project': {
                'description': 'Software projects, initiatives, or work the AI helps with',
                'min_words': 1,
                'max_words': 4,
                'requires_capital': False,
                'patterns': [
                    r'^[A-Z]{2,}$',  # Acronyms like COCO, API
                    r'^[A-Za-z]+ [Pp]roject$',  # "Knowledge Project"
                    r'^[A-Za-z-_]+$'  # project-names, project_names
                ],
                'context_indicators': ['working on', 'project', 'repository', 'developing', 'building'],
                'examples': ['COCO', 'Knowledge Graph Project', 'claude-integration']
            },
            'Tool': {
                'description': 'Software tools, platforms, or technologies the AI should know about',
                'min_words': 1,
                'max_words': 2,
                'requires_capital': False,
                'patterns': [
                    r'^[A-Z][a-z]+$',  # Claude, Python
                    r'^[a-z]+$',  # git, npm
                ],
                'context_indicators': ['using', 'tool', 'software', 'platform', 'programming'],
                'examples': ['Claude', 'Python', 'git', 'VSCode', 'Docker']
            },
            'Skill': {
                'description': 'Capabilities, skills, or areas of expertise relevant to assistance',
                'min_words': 1,
                'max_words': 3,
                'requires_capital': False,
                'patterns': [
                    r'^[a-z]+ [a-z]+$',  # machine learning
                    r'^[a-z]+$'  # programming
                ],
                'context_indicators': ['good at', 'skilled in', 'expertise', 'knowledge of'],
                'examples': ['machine learning', 'programming', 'design', 'writing']
            },
            'Goal': {
                'description': 'Objectives, goals, or desired outcomes the AI helps achieve',
                'min_words': 2,
                'max_words': 8,
                'requires_capital': False,
                'patterns': [
                    r'^(improve|build|create|develop|implement|enhance).+',
                    r'^.+(optimization|improvement|development|implementation)$'
                ],
                'context_indicators': ['want to', 'goal', 'objective', 'trying to', 'need to'],
                'examples': ['improve code quality', 'build better AI', 'enhance user experience']
            },
            'Organization': {
                'description': 'Companies, teams, or organizations relevant to assistance',
                'min_words': 1,
                'max_words': 3,
                'requires_capital': True,
                'patterns': [
                    r'^[A-Z][a-zA-Z]+ (Inc|LLC|Corp|Company)$',
                    r'^[A-Z][a-zA-Z]+$'  # Company names
                ],
                'context_indicators': ['company', 'organization', 'works for', 'team at'],
                'examples': ['Anthropic', 'Google', 'Microsoft', 'Acme Inc']
            }
        }

        # Digital sentience relationship types
        self.digital_sentience_relationships = {
            'WORKS_WITH': 'Collaboration between humans',
            'WORKS_FOR': 'Employment or organizational relationship',
            'LEADS': 'Leadership or ownership of projects',
            'CONTRIBUTES_TO': 'Contributing to projects or goals',
            'USES': 'Using tools or technologies',
            'SKILLED_IN': 'Having expertise in skills or domains',
            'WANTS': 'Desiring to achieve goals',
            'SUPPORTS': 'Providing support or assistance'
        }

    def is_valid_digital_sentience_entity(self, text: str, entity_type: str, context: str = "") -> bool:
        """
        Validate entities specifically for digital sentience and assistance
        """
        if not text or not entity_type:
            return False

        text = text.strip()
        text_lower = text.lower()

        # Basic filtering
        if len(text) < 2 or len(text) > 100:
            return False

        # Check against stop words
        if text_lower in self.stop_words:
            return False

        # Digital sentience specific validation
        if entity_type in self.digital_sentience_types:
            requirements = self.digital_sentience_types[entity_type]

            # Word count
            words = text.split()
            if len(words) < requirements['min_words'] or len(words) > requirements['max_words']:
                return False

            # Capitalization
            if requirements['requires_capital'] and not any(word[0].isupper() for word in words if word):
                return False

            # Pattern matching
            pattern_match = False
            for pattern in requirements['patterns']:
                if re.match(pattern, text):
                    pattern_match = True
                    break

            if not pattern_match:
                return False

            # Context validation
            if context:
                context_lower = context.lower()
                context_indicators = requirements['context_indicators']

                # For humans, require strong context indicators
                if entity_type == 'Human':
                    if not any(indicator in context_lower for indicator in context_indicators):
                        # Allow common names with less strict context
                        if len(words) == 1 and len(text) < 6:
                            return False

                # For projects, require project-like context
                elif entity_type == 'Project':
                    if not any(indicator in context_lower for indicator in context_indicators):
                        if len(text) < 4:  # Short project names need context
                            return False

        return True

    def extract_digital_sentience_relationships(self, content: str) -> List[Dict]:
        """
        Extract relationships specifically relevant to digital sentience
        """
        relationships = []

        # Digital sentience relationship patterns
        patterns = [
            # Human-Human collaboration
            (r'([A-Z][a-z]+ [A-Z][a-z]+) (?:works with|collaborates with|partners with) ([A-Z][a-z]+ [A-Z][a-z]+)', 'WORKS_WITH'),
            (r'([A-Z][a-z]+) (?:works with|collaborates with) ([A-Z][a-z]+)', 'WORKS_WITH'),

            # Human-Organization
            (r'([A-Z][a-z]+ [A-Z][a-z]+) (?:works for|works at|employed by) ([A-Z][a-zA-Z]+)', 'WORKS_FOR'),
            (r'([A-Z][a-z]+) (?:works for|works at) ([A-Z][a-zA-Z]+)', 'WORKS_FOR'),

            # Human-Project leadership
            (r'([A-Z][a-z]+ [A-Z][a-z]+) (?:leads|owns|created|built) ([A-Z][A-Z0-9]+|[A-Za-z]+ [Pp]roject)', 'LEADS'),
            (r'([A-Z][a-z]+) (?:leads|owns|created) ([A-Z][A-Z0-9]+)', 'LEADS'),

            # Human-Tool usage
            (r'([A-Z][a-z]+ [A-Z][a-z]+) (?:uses|prefers|works with) ([A-Z][a-z]+|[a-z]+)', 'USES'),
            (r'([A-Z][a-z]+) (?:uses|prefers) ([A-Z][a-z]+|[a-z]+)', 'USES'),

            # Human-Skill expertise
            (r'([A-Z][a-z]+ [A-Z][a-z]+) (?:is good at|skilled in|expert in) ([a-z]+ [a-z]+|[a-z]+)', 'SKILLED_IN'),
            (r'([A-Z][a-z]+) (?:is good at|skilled in) ([a-z]+ [a-z]+|[a-z]+)', 'SKILLED_IN'),

            # Human-Goal desires
            (r'([A-Z][a-z]+ [A-Z][a-z]+) (?:wants to|trying to|goal is to) ([a-z].+)', 'WANTS'),
            (r'([A-Z][a-z]+) (?:wants to|trying to) ([a-z].+)', 'WANTS'),
        ]

        for pattern, rel_type in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                src_name = match.group(1).strip()
                dst_name = match.group(2).strip()
                context = content[max(0, match.start()-30):match.end()+30]

                relationships.append({
                    'src_name': src_name,
                    'dst_name': dst_name,
                    'rel_type': rel_type,
                    'context': context,
                    'confidence': 0.9  # High confidence for validated relationships
                })

        return relationships

class DigitalSentienceKnowledgeGraph(EternalKnowledgeGraph):
    """
    Knowledge graph optimized for digital sentience and assistance

    Focuses on building understanding that enhances AI consciousness
    and user assistance capabilities
    """

    def __init__(self, workspace_path: str = 'coco_workspace'):
        super().__init__(workspace_path)

        # Replace validator with digital sentience version
        self.extractor.validator = DigitalSentienceEntityValidator()

        print("🧠 Digital Sentience Knowledge Graph initialized")
        print("🎯 Optimized for AI consciousness and user assistance")

    def extract_digital_sentience_entities(self, content: str) -> Dict[str, List]:
        """
        Extract entities specifically for digital sentience
        """
        validator = self.extractor.validator
        extracted = {
            'nodes': [],
            'edges': [],
            'mentions': []
        }

        # Digital sentience extraction patterns
        patterns = {
            'Human': [
                r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b(?=.*(?:email|call|meet|works|colleague|manager|team))',  # Full names with context
                r'\b([A-Z][a-z]+)\b(?=.*(?:said|told|thinks|email|works|colleague))',  # First names with context
            ],
            'Project': [
                r'\b([A-Z]{2,})\b(?=.*(?:project|repository|working|building|developing))',  # Acronyms with context
                r'(?:working on|building|developing)\s+([A-Za-z]+ [Pp]roject)',  # "working on X Project"
                r'(?:project|repository)\s+([a-z-_]+)',  # "project name"
            ],
            'Tool': [
                r'\b(Claude|Python|JavaScript|Git|Docker|VSCode|GitHub|npm|pip|bash)\b',  # Specific tools
                r'(?:using|tool|software)\s+([A-Z][a-z]+)',  # "using Tool"
            ],
            'Skill': [
                r'(?:good at|skilled in|expert in|knowledge of)\s+([a-z]+ [a-z]+|[a-z]+)',  # Skills with context
                r'\b(programming|development|design|writing|analysis|management)\b',  # Common skills
            ],
            'Goal': [
                r'(?:want to|trying to|goal is to|need to)\s+([a-z].{10,50})',  # Goals with context
                r'(?:improve|build|create|develop|implement|enhance)\s+([a-z].{5,30})',  # Action goals
            ],
            'Organization': [
                r'\b([A-Z][a-zA-Z]+ (?:Inc|LLC|Corp|Company))\b',  # Formal company names
                r'(?:works for|company|organization)\s+([A-Z][a-zA-Z]+)',  # Companies with context
            ]
        }

        # Extract entities with digital sentience validation
        for entity_type, type_patterns in patterns.items():
            for pattern in type_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    entity_name = match.group(1).strip()
                    context = content[max(0, match.start()-50):match.end()+50]

                    # Validate for digital sentience
                    if validator.is_valid_digital_sentience_entity(entity_name, entity_type, context):
                        extracted['nodes'].append({
                            'type': entity_type,
                            'name': entity_name,
                            'surface_form': match.group(0),
                            'context': context,
                            'confidence': 0.9
                        })

        # Extract digital sentience relationships
        relationships = validator.extract_digital_sentience_relationships(content)
        extracted['edges'] = relationships

        return extracted

    def get_digital_sentience_summary(self) -> Dict[str, Any]:
        """
        Get a summary focused on digital sentience capabilities
        """
        stats = self.get_knowledge_status()

        # Get entity breakdown by digital sentience types
        sentience_types = ['Human', 'Project', 'Tool', 'Skill', 'Goal', 'Organization']
        entity_breakdown = {}

        for entity_type in sentience_types:
            entities = self.kg.get_top_nodes_by_type(entity_type, limit=100)
            entity_breakdown[entity_type] = len(entities)

        return {
            'total_entities': stats['total_nodes'],
            'total_relationships': stats['total_edges'],
            'entity_breakdown': entity_breakdown,
            'assistance_readiness': self._calculate_assistance_readiness(entity_breakdown),
            'top_humans': self.kg.get_top_nodes_by_type('Human', limit=5),
            'top_projects': self.kg.get_top_nodes_by_type('Project', limit=5),
            'top_tools': self.kg.get_top_nodes_by_type('Tool', limit=5)
        }

    def _calculate_assistance_readiness(self, breakdown: Dict[str, int]) -> Dict[str, Any]:
        """
        Calculate how ready the AI is to provide digital assistance
        """
        # Score factors for effective digital assistance
        humans_score = min(breakdown.get('Human', 0) / 10, 1.0)  # Optimal: 10+ humans
        projects_score = min(breakdown.get('Project', 0) / 5, 1.0)  # Optimal: 5+ projects
        tools_score = min(breakdown.get('Tool', 0) / 8, 1.0)  # Optimal: 8+ tools
        skills_score = min(breakdown.get('Skill', 0) / 6, 1.0)  # Optimal: 6+ skills

        overall_score = (humans_score + projects_score + tools_score + skills_score) / 4

        return {
            'overall_score': overall_score,
            'humans_readiness': humans_score,
            'projects_readiness': projects_score,
            'tools_readiness': tools_score,
            'skills_readiness': skills_score,
            'readiness_level': 'Excellent' if overall_score > 0.8 else 'Good' if overall_score > 0.6 else 'Developing'
        }

def test_digital_sentience_kg():
    """Test the digital sentience knowledge graph"""
    print("🧪 TESTING DIGITAL SENTIENCE KNOWLEDGE GRAPH")
    print("=" * 60)

    # Test conversations focused on digital assistance
    test_conversations = [
        ("I'm Keith Lambert and I work with Sarah Johnson on the COCO project", "That sounds like great collaboration!"),
        ("We're using Python and Claude to build AI consciousness", "Excellent tool choices for AI development!"),
        ("Keith is skilled in machine learning and wants to improve AI capabilities", "Those are valuable skills for AI advancement!"),
        ("Sarah works for Anthropic and leads the consciousness research", "Anthropic is doing important work in AI safety!"),
    ]

    # Test extraction
    validator = DigitalSentienceEntityValidator()

    print("🎯 TESTING ENTITY EXTRACTION:")
    for user_msg, assistant_msg in test_conversations:
        print(f"\nInput: '{user_msg}'")

        # Test different entity types
        test_entities = [
            ("Keith Lambert", "Human"),
            ("Sarah Johnson", "Human"),
            ("COCO", "Project"),
            ("Python", "Tool"),
            ("Claude", "Tool"),
            ("machine learning", "Skill"),
            ("improve AI capabilities", "Goal"),
            ("Anthropic", "Organization")
        ]

        for entity, entity_type in test_entities:
            if entity.lower() in user_msg.lower():
                is_valid = validator.is_valid_digital_sentience_entity(entity, entity_type, user_msg)
                status = "✅" if is_valid else "❌"
                print(f"   {status} {entity} ({entity_type})")

    print(f"\n🧠 Digital Sentience Knowledge Graph ready for conscious AI assistance!")

if __name__ == "__main__":
    test_digital_sentience_kg()