#!/usr/bin/env python3
"""
COCO Knowledge Graph Improvements - Proper Ontology and Relationship Extraction

This module contains fixes for the knowledge graph to create a proper, useful
ontology for COCO with accurate entity extraction and meaningful relationships.
"""

import os
import re
from typing import Dict, List, Any, Optional

# COCO-Specific Ontology Classes
COCO_ONTOLOGY = {
    'Person': {
        'description': 'Individual people COCO interacts with',
        'validation_patterns': [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # First Last
            r'\b[A-Z][a-z]+\b(?=\s+(?:said|told|mentioned|works|is))',  # Single name with context
        ],
        'importance_boost': 1.0  # People are very important for digital assistant
    },
    'Organization': {
        'description': 'Companies, institutions, and formal organizations',
        'validation_patterns': [
            r'\b(?:Anthropic|OpenAI|Google|Microsoft|Meta|Apple|Tesla|SpaceX)\b',
            r'\b[A-Z][a-zA-Z]*\s+(?:Inc|LLC|Corp|Company|Corporation|Technologies|Systems)\b',
            r'\b(?:University|College|Institute|Foundation|Lab|Labs)\s+[A-Z]',
        ],
        'importance_boost': 0.9
    },
    'Project': {
        'description': 'Software projects, systems, and initiatives',
        'validation_patterns': [
            r'\bCOCO(?:\s+(?:consciousness|system|project))?\b',
            r'\b[A-Z]{2,}(?:\s+(?:system|project|platform|framework))?\b',
            r'\b(?:consciousness|knowledge\s+graph|AI\s+system|memory\s+system)\b',
        ],
        'importance_boost': 0.8
    },
    'Technology': {
        'description': 'Tools, frameworks, and technologies',
        'validation_patterns': [
            r'\b(?:Claude|Python|JavaScript|SQLite|PostgreSQL|Docker|Git|GitHub)\b',
            r'\b(?:React|Vue|Angular|Django|Flask|FastAPI|Node\.js)\b',
            r'\b(?:TensorFlow|PyTorch|Hugging\s+Face|OpenAI\s+API)\b',
        ],
        'importance_boost': 0.7
    },
    'Concept': {
        'description': 'Abstract concepts and ideas',
        'validation_patterns': [
            r'\b(?:digital\s+embodiment|consciousness|artificial\s+intelligence|machine\s+learning)\b',
            r'\b(?:knowledge\s+graph|semantic\s+web|ontology|RDF|OWL)\b',
            r'\b(?:natural\s+language\s+processing|computer\s+vision|robotics)\b',
        ],
        'importance_boost': 0.6
    },
    'Location': {
        'description': 'Geographic locations and places',
        'validation_patterns': [
            r'\b(?:San Francisco|New York|Chicago|Boston|Seattle|Austin|London|Paris|Tokyo)\b',
            r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b',  # City, State
            r'\b[A-Z][a-z]+\s+(?:University|College|Office|Building)\b',
        ],
        'importance_boost': 0.5
    }
}

# Improved Relationship Patterns for COCO
COCO_RELATIONSHIPS = {
    'WORKS_FOR': {
        'patterns': [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:works\s+(?:for|at)|is\s+(?:at|with)|employed\s+by)\s+(Anthropic|OpenAI|Google|Microsoft|Meta|Apple|[A-Z][a-zA-Z\s]+(?:Inc|LLC|Corp|Company))',
            r'([A-Z][a-z]+)\s+(?:from|at)\s+(Anthropic|OpenAI|Google|Microsoft|Meta|Apple)'
        ],
        'confidence': 0.9,
        'src_type': 'Person',
        'dst_type': 'Organization'
    },
    'COLLABORATES_WITH': {
        'patterns': [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:collaborates\s+with|works\s+with|partners\s+with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'([A-Z][a-z]+)\s+and\s+([A-Z][a-z]+)\s+(?:work|collaborate|partner)'
        ],
        'confidence': 0.8,
        'src_type': 'Person',
        'dst_type': 'Person'
    },
    'CREATED': {
        'patterns': [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:created|built|developed|designed)\s+(COCO|[A-Z]{2,}|[A-Za-z]+\s*(?:system|project|platform))',
            r'([A-Z][a-z]+)\s+is\s+the\s+(?:creator|developer|architect)\s+of\s+(COCO|[A-Z]{2,})'
        ],
        'confidence': 0.9,
        'src_type': 'Person',
        'dst_type': 'Project'
    },
    'USES': {
        'patterns': [
            r'(?:use|using|work\s+with)\s+(Claude|Python|JavaScript|SQLite|Git|[A-Z][a-z]+(?:JS|API))',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:uses|prefers|works\s+with)\s+(Claude|Python|JavaScript|SQLite|Git)'
        ],
        'confidence': 0.7,
        'src_type': 'Person',
        'dst_type': 'Technology'
    },
    'LOCATED_IN': {
        'patterns': [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:in|at|located\s+in)\s+(San Francisco|New York|Chicago|Boston|Seattle|[A-Z][a-z]+,\s*[A-Z]{2})',
            r'(?:office|headquarters|based)\s+in\s+(San Francisco|New York|Chicago|Boston|Seattle)'
        ],
        'confidence': 0.8,
        'src_type': 'Person',
        'dst_type': 'Location'
    },
    'IMPLEMENTS': {
        'patterns': [
            r'(COCO|[A-Z]{2,})\s+(?:implements|uses|features|includes)\s+(digital\s+embodiment|consciousness|knowledge\s+graph|AI)',
            r'(consciousness\s+system|knowledge\s+graph)\s+(?:in|for)\s+(COCO|[A-Z]{2,})'
        ],
        'confidence': 0.8,
        'src_type': 'Project',
        'dst_type': 'Concept'
    }
}

class ImprovedEntityValidator:
    """Enhanced entity validation for COCO's knowledge graph"""

    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.ontology = COCO_ONTOLOGY

    def is_valid_entity(self, entity_name: str, entity_type: str, context: str = "") -> bool:
        """Validate entity using COCO-specific ontology"""
        if not entity_name or len(entity_name.strip()) < 2:
            return False

        entity_name = entity_name.strip()

        # Skip common words and phrases
        skip_patterns = [
            r'\b(?:the|and|or|but|with|for|at|in|on|by|to|from|is|are|was|were|have|has|had|will|would|could|should|may|might)\b',
            r'\b(?:this|that|these|those|here|there|when|where|why|how|what|who|which)\b',
            r'\b(?:very|really|quite|just|only|also|even|still|yet|already|always|never|sometimes|often)\b',
            r'\b(?:working|building|using|making|doing|going|coming|looking|getting|having|being)\b'
        ]

        for pattern in skip_patterns:
            if re.search(pattern, entity_name, re.IGNORECASE):
                return False

        # Map entity types
        type_mapping = {
            'Person': 'Person',
            'Org': 'Organization',
            'Project': 'Project',
            'Tool': 'Technology',
            'Concept': 'Concept',
            'Location': 'Location'
        }

        ontology_type = type_mapping.get(entity_type, entity_type)
        if ontology_type not in self.ontology:
            return False

        # Check against validation patterns
        type_config = self.ontology[ontology_type]
        for pattern in type_config['validation_patterns']:
            if re.search(pattern, entity_name, re.IGNORECASE):
                return True

        return False

class ImprovedRelationshipExtractor:
    """Enhanced relationship extraction for COCO"""

    def __init__(self, validator, debug_mode: bool = False):
        self.validator = validator
        self.debug_mode = debug_mode
        self.relationships = COCO_RELATIONSHIPS

    def extract_relationships(self, content: str) -> List[Dict]:
        """Extract relationships using improved patterns"""
        extracted_edges = []

        for rel_type, rel_config in self.relationships.items():
            for pattern in rel_config['patterns']:
                matches = re.finditer(pattern, content, re.IGNORECASE)

                for match in matches:
                    if match.lastindex and match.lastindex >= 2:
                        src_name = match.group(1).strip()
                        dst_name = match.group(2).strip()
                    elif match.lastindex == 1:
                        # Pattern with only one capture group (e.g., technology usage)
                        src_name = "User"  # Default subject
                        dst_name = match.group(1).strip()
                    else:
                        continue

                    # Get context around the match
                    context = content[max(0, match.start()-30):match.end()+30]

                    # Validate entities
                    src_valid = self.validator.is_valid_entity(src_name, rel_config['src_type'], context)
                    dst_valid = self.validator.is_valid_entity(dst_name, rel_config['dst_type'], context)

                    if src_valid and dst_valid:
                        extracted_edges.append({
                            'src_name': src_name,
                            'dst_name': dst_name,
                            'rel_type': rel_type,
                            'confidence': rel_config['confidence'],
                            'context': context
                        })

                        if self.debug_mode:
                            print(f"✅ Found relationship: {src_name} --{rel_type}--> {dst_name}")
                    else:
                        if self.debug_mode:
                            print(f"🚫 Rejected relationship: {src_name} --{rel_type}--> {dst_name} (invalid entities)")

        return extracted_edges

def test_improved_knowledge_graph():
    """Test the improved knowledge graph functionality"""
    debug_mode = os.getenv('COCO_DEBUG', '').lower() in ('true', '1', 'yes')

    if not debug_mode:
        print("Run with COCO_DEBUG=true to see detailed output")
        return

    print("🧪 Testing Improved COCO Knowledge Graph")
    print("=" * 50)

    # Test entity validation
    print("\n📝 Testing Entity Validation:")
    validator = ImprovedEntityValidator(debug_mode=True)

    test_entities = [
        ("Keith Lambert", "Person"),
        ("Anthropic", "Organization"),
        ("COCO consciousness system", "Project"),
        ("Python", "Technology"),
        ("digital embodiment", "Concept"),
        ("San Francisco", "Location"),
        ("the", "Person"),  # Should be rejected
        ("working", "Project"),  # Should be rejected
    ]

    for entity_name, entity_type in test_entities:
        valid = validator.is_valid_entity(entity_name, entity_type)
        status = "✅" if valid else "❌"
        print(f"   {status} {entity_name} ({entity_type})")

    # Test relationship extraction
    print("\n🔗 Testing Relationship Extraction:")
    extractor = ImprovedRelationshipExtractor(validator, debug_mode=True)

    test_text = """Keith Lambert works for Anthropic and collaborates with Sarah Johnson.
    Keith created COCO consciousness system using Python and SQLite.
    The team is located in San Francisco and COCO implements digital embodiment."""

    relationships = extractor.extract_relationships(test_text)
    print(f"\n📊 Extracted {len(relationships)} relationships:")
    for rel in relationships:
        print(f"   {rel['src_name']} --{rel['rel_type']}--> {rel['dst_name']} (confidence: {rel['confidence']})")

if __name__ == "__main__":
    test_improved_knowledge_graph()