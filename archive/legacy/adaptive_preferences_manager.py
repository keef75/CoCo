#!/usr/bin/env python3
"""
COCO Adaptive Preferences Manager
=================================
Implements Layer 1 of the 4-layer memory architecture - adaptive preferences system
that enables COCO to evolve based on user feedback and stated preferences.

This extends the existing markdown identity system (COCO.md, USER_PROFILE.md)
with intelligent preference learning and behavioral adaptation.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class PreferenceSignal:
    """Detected preference or feedback signal from user interaction."""
    signal_type: str  # 'positive_feedback', 'negative_feedback', 'specific_instruction', 'format_preference'
    content: str
    context: str
    timestamp: datetime
    confidence: float

class AdaptivePreferencesManager:
    """
    Enhanced Layer 1 manager that adds adaptive learning to COCO's identity system.

    Builds on existing COCO.md, USER_PROFILE.md, previous_conversation.md files
    and adds intelligent preference tracking through preferences.md.
    """

    def __init__(self, workspace_path: str = "./coco_workspace"):
        self.workspace = Path(workspace_path)
        self.max_tokens = 10000  # Layer 1 budget

        # Identity files (existing + new preferences)
        self.identity_files = {
            'coco': self.workspace / 'COCO.md',
            'user': self.workspace / 'USER_PROFILE.md',
            'conversation': self.workspace / 'previous_conversation.md',
            'preferences': self.workspace / 'preferences.md'  # NEW: Adaptive preferences
        }

        # Preference learning patterns
        self.feedback_patterns = {
            'positive': [
                r"great job", r"perfect", r"exactly", r"i like", r"i love",
                r"that's awesome", r"well done", r"excellent", r"that works",
                r"amazing", r"brilliant", r"wonderful", r"fantastic"
            ],
            'negative': [
                r"not quite", r"don't like", r"wrong format", r"try again",
                r"that's not", r"please don't", r"stop doing", r"avoid"
            ],
            'instruction': [
                r"always", r"never", r"from now on", r"make sure to",
                r"remember to", r"every time", r"when you", r"please"
            ],
            'format': [
                r"format", r"style", r"use bullets", r"numbered list",
                r"include code", r"add examples", r"be brief", r"more detail"
            ]
        }

        # Initialize preferences file if needed
        self._initialize_preferences_file()

    def _initialize_preferences_file(self):
        """Initialize preferences.md with structured sections."""
        if not self.identity_files['preferences'].exists():
            initial_content = f"""# COCO Learned Preferences
## Initialized: {datetime.now().isoformat()}

### Communication Preferences
*Learn from: "I prefer...", "I like when you...", positive feedback*

### Output Formatting Preferences
*Learn from: format-specific feedback, style requests*

### Task Execution Preferences
*Learn from: "always do X", "remember to Y", workflow feedback*

### Behavioral Adaptations
*Learn from: interaction patterns, success/failure feedback*

### Specific User Instructions
*Learn from: explicit instructions like "always include...", "never do..."*

### Feedback Learning Log
*Automatic tracking of all preference signals for analysis*

### Preference Evolution Timeline
*Track how preferences change over time*

---
*This file automatically evolves as COCO learns from user interactions*
"""
            self.identity_files['preferences'].write_text(initial_content)

    def extract_preference_signals(self, user_input: str, assistant_response: str = "") -> List[PreferenceSignal]:
        """
        Extract preference signals from user interaction.

        This is the core intelligence that detects when users express preferences,
        give feedback, or provide instructions that should be remembered.
        """
        signals = []
        input_lower = user_input.lower()

        # Check for positive feedback signals
        for pattern in self.feedback_patterns['positive']:
            if re.search(pattern, input_lower):
                signals.append(PreferenceSignal(
                    signal_type='positive_feedback',
                    content=user_input,
                    context=assistant_response[:200] if assistant_response else "",
                    timestamp=datetime.now(),
                    confidence=0.8
                ))
                break  # Only one positive signal per input

        # Check for negative feedback signals
        for pattern in self.feedback_patterns['negative']:
            if re.search(pattern, input_lower):
                signals.append(PreferenceSignal(
                    signal_type='negative_feedback',
                    content=user_input,
                    context=assistant_response[:200] if assistant_response else "",
                    timestamp=datetime.now(),
                    confidence=0.9
                ))
                break

        # Check for specific instructions
        for pattern in self.feedback_patterns['instruction']:
            if re.search(pattern, input_lower):
                signals.append(PreferenceSignal(
                    signal_type='specific_instruction',
                    content=user_input,
                    context="",
                    timestamp=datetime.now(),
                    confidence=0.95
                ))
                break

        # Check for format preferences
        for pattern in self.feedback_patterns['format']:
            if re.search(pattern, input_lower):
                signals.append(PreferenceSignal(
                    signal_type='format_preference',
                    content=user_input,
                    context=assistant_response[:200] if assistant_response else "",
                    timestamp=datetime.now(),
                    confidence=0.7
                ))
                break

        return signals

    def update_preferences(self, signals: List[PreferenceSignal]):
        """
        Update preferences.md based on detected signals.

        This is where COCO's adaptive learning happens - preference signals
        are processed and integrated into permanent behavioral guidelines.
        """
        if not signals:
            return

        current_content = self.identity_files['preferences'].read_text()
        sections = self._parse_preference_sections(current_content)

        for signal in signals:
            timestamp = signal.timestamp.strftime("%Y-%m-%d %H:%M")
            confidence_indicator = "🔥" if signal.confidence >= 0.9 else "✅" if signal.confidence >= 0.8 else "📝"

            if signal.signal_type == 'positive_feedback':
                # Extract what COCO did that the user liked
                behavior = self._extract_successful_behavior(signal.content, signal.context)
                if behavior:
                    entry = f"- [{timestamp}] {confidence_indicator} User appreciated: {behavior}"
                    sections['Communication Preferences'].append(entry)

            elif signal.signal_type == 'negative_feedback':
                # Extract what to avoid
                avoid_behavior = self._extract_negative_behavior(signal.content)
                if avoid_behavior:
                    entry = f"- [{timestamp}] ❌ Avoid: {avoid_behavior}"
                    sections['Behavioral Adaptations'].append(entry)

            elif signal.signal_type == 'specific_instruction':
                # Direct user instruction
                instruction = signal.content.strip()
                entry = f"- [{timestamp}] 🎯 Instruction: {instruction}"
                sections['Specific User Instructions'].append(entry)

            elif signal.signal_type == 'format_preference':
                # Format/style preference
                format_pref = self._extract_format_preference(signal.content)
                if format_pref:
                    entry = f"- [{timestamp}] 🎨 Format: {format_pref}"
                    sections['Output Formatting Preferences'].append(entry)

            # Always log to learning log for analysis
            log_entry = f"- [{timestamp}] {signal.signal_type}: {signal.content[:100]}... (confidence: {signal.confidence:.2f})"
            sections['Feedback Learning Log'].append(log_entry)

        # Reconstruct and save
        updated_content = self._reconstruct_preferences(sections)
        self.identity_files['preferences'].write_text(updated_content)

    def load_identity_context(self) -> str:
        """
        Load complete Layer 1 context with token budget management.

        Assembles all identity files into coherent context that defines
        COCO's identity, user understanding, and learned preferences.
        """
        context_parts = [
            "=== LAYER 1: IDENTITY & ADAPTIVE PREFERENCES ===",
            f"Context loaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Token budget: {self.max_tokens:,} tokens",
            ""
        ]

        # Load files in priority order (most important first)
        files_to_load = [
            ('preferences', 'Adaptive Preferences'),
            ('coco', 'Core Identity'),
            ('user', 'User Profile'),
            ('conversation', 'Previous Session Summary')
        ]

        current_tokens = self._estimate_tokens("\n".join(context_parts))

        for file_key, section_name in files_to_load:
            if current_tokens >= self.max_tokens * 0.9:  # Leave 10% buffer
                break

            file_path = self.identity_files[file_key]
            if file_path.exists():
                content = file_path.read_text()
                content_tokens = self._estimate_tokens(content)

                if current_tokens + content_tokens <= self.max_tokens:
                    context_parts.append(f"## {section_name}")
                    context_parts.append(content)
                    context_parts.append("")
                    current_tokens += content_tokens
                else:
                    # Truncate to fit budget
                    available_tokens = self.max_tokens - current_tokens - 100  # Buffer
                    truncated_content = self._truncate_to_tokens(content, available_tokens)
                    context_parts.append(f"## {section_name} (Truncated)")
                    context_parts.append(truncated_content)
                    context_parts.append("")
                    break

        return "\n".join(context_parts)

    def analyze_preference_evolution(self) -> Dict[str, any]:
        """
        Analyze how preferences have evolved over time.

        Provides insights into COCO's learning progress and adaptation patterns.
        """
        if not self.identity_files['preferences'].exists():
            return {'status': 'no_preferences_file'}

        content = self.identity_files['preferences'].read_text()

        # Extract timestamps and preference types
        timestamp_pattern = r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\]'
        timestamps = re.findall(timestamp_pattern, content)

        # Count preference types
        positive_count = len(re.findall(r'appreciated:', content))
        negative_count = len(re.findall(r'Avoid:', content))
        instruction_count = len(re.findall(r'Instruction:', content))
        format_count = len(re.findall(r'Format:', content))

        # Calculate learning velocity (preferences per day)
        if timestamps:
            first_timestamp = datetime.strptime(timestamps[0], '%Y-%m-%d %H:%M')
            last_timestamp = datetime.strptime(timestamps[-1], '%Y-%m-%d %H:%M')
            days_span = (last_timestamp - first_timestamp).days or 1
            learning_velocity = len(timestamps) / days_span
        else:
            learning_velocity = 0

        return {
            'total_preferences': len(timestamps),
            'positive_feedback': positive_count,
            'negative_feedback': negative_count,
            'instructions': instruction_count,
            'format_preferences': format_count,
            'learning_velocity': round(learning_velocity, 2),
            'latest_update': timestamps[-1] if timestamps else None
        }

    def get_active_preferences_summary(self) -> str:
        """
        Generate a concise summary of currently active preferences.

        Used for quick reference in context assembly.
        """
        if not self.identity_files['preferences'].exists():
            return "No learned preferences yet."

        content = self.identity_files['preferences'].read_text()

        # Extract recent high-confidence preferences (last 30 days)
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_prefs = []

        lines = content.split('\n')
        for line in lines:
            if re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\]', line):
                timestamp_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\]', line)
                if timestamp_match:
                    timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M')
                    if timestamp > cutoff_date and ('🔥' in line or '🎯' in line):
                        recent_prefs.append(line.strip())

        if recent_prefs:
            return "**Active Preferences:**\n" + "\n".join(recent_prefs[:10])
        else:
            return "Learning preferences through interaction..."

    def _parse_preference_sections(self, content: str) -> Dict[str, List[str]]:
        """Parse preferences.md into structured sections."""
        sections = {
            'Communication Preferences': [],
            'Output Formatting Preferences': [],
            'Task Execution Preferences': [],
            'Behavioral Adaptations': [],
            'Specific User Instructions': [],
            'Feedback Learning Log': [],
            'Preference Evolution Timeline': []
        }

        current_section = None
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('### '):
                section_name = line[4:].strip()
                if section_name in sections:
                    current_section = section_name
            elif current_section and line.startswith('- '):
                sections[current_section].append(line)

        return sections

    def _reconstruct_preferences(self, sections: Dict[str, List[str]]) -> str:
        """Reconstruct preferences.md from parsed sections."""
        content_parts = [
            f"# COCO Learned Preferences",
            f"## Last Updated: {datetime.now().isoformat()}",
            ""
        ]

        for section_name, items in sections.items():
            content_parts.append(f"### {section_name}")

            if items:
                # Keep only recent items to manage file size
                recent_items = items[-50:] if len(items) > 50 else items
                content_parts.extend(recent_items)
            else:
                content_parts.append("*No preferences learned yet*")

            content_parts.append("")

        content_parts.append("---")
        content_parts.append("*This file automatically evolves as COCO learns from user interactions*")

        return "\n".join(content_parts)

    def _extract_successful_behavior(self, feedback: str, context: str) -> Optional[str]:
        """Extract what COCO did that the user appreciated."""
        # Look for specific behaviors mentioned in context
        behaviors = []

        if "format" in feedback.lower() and context:
            if "```" in context:
                behaviors.append("using code blocks")
            if "- " in context:
                behaviors.append("using bullet points")
            if "\n1." in context:
                behaviors.append("using numbered lists")

        if "explain" in feedback.lower():
            behaviors.append("providing detailed explanations")

        if "example" in feedback.lower() and context:
            behaviors.append("including examples")

        return behaviors[0] if behaviors else None

    def _extract_negative_behavior(self, feedback: str) -> Optional[str]:
        """Extract what behavior to avoid based on negative feedback."""
        feedback_lower = feedback.lower()

        if "too long" in feedback_lower or "too verbose" in feedback_lower:
            return "being too verbose"
        elif "too short" in feedback_lower or "more detail" in feedback_lower:
            return "being too brief"
        elif "wrong format" in feedback_lower:
            return "using incorrect formatting"
        elif "don't" in feedback_lower:
            # Extract the "don't" instruction
            dont_match = re.search(r"don't\s+(\w+(?:\s+\w+){0,3})", feedback_lower)
            if dont_match:
                return dont_match.group(1)

        return feedback  # Return original if no specific pattern found

    def _extract_format_preference(self, content: str) -> Optional[str]:
        """Extract formatting preference from user input."""
        content_lower = content.lower()

        if "bullet" in content_lower or "list" in content_lower:
            return "use bullet points for lists"
        elif "number" in content_lower:
            return "use numbered lists"
        elif "code block" in content_lower or "```" in content:
            return "use code blocks for code"
        elif "brief" in content_lower or "concise" in content_lower:
            return "be concise and brief"
        elif "detail" in content_lower or "thorough" in content_lower:
            return "provide detailed explanations"

        return content  # Return original if no specific pattern

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (4 characters ≈ 1 token)."""
        return len(text) // 4

    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token budget."""
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text

        # Try to truncate at paragraph boundary
        truncated = text[:max_chars]
        last_paragraph = truncated.rfind('\n\n')
        if last_paragraph > max_chars * 0.8:  # If we can save 80% of content
            return truncated[:last_paragraph] + "\n\n[Content truncated to fit token budget]"
        else:
            return truncated[:max_chars-50] + "\n\n[Content truncated to fit token budget]"


# Test the adaptive preferences system
if __name__ == "__main__":
    print("🧠 Testing COCO Adaptive Preferences Manager")
    print("=" * 60)

    # Initialize manager
    manager = AdaptivePreferencesManager()

    # Test preference signal extraction
    test_cases = [
        ("Great job on that email format!", "I sent an email with bullet points..."),
        ("I love how you explained that with examples", "Here's an example of how it works..."),
        ("Always include code comments when you write code", ""),
        ("Please don't make responses so long", ""),
        ("Use numbered lists for step-by-step instructions", "")
    ]

    for user_input, assistant_response in test_cases:
        signals = manager.extract_preference_signals(user_input, assistant_response)
        print(f"\nInput: '{user_input}'")
        for signal in signals:
            print(f"  → {signal.signal_type}: {signal.confidence:.2f} confidence")

        # Update preferences with detected signals
        manager.update_preferences(signals)

    # Test context loading
    context = manager.load_identity_context()
    print(f"\n✅ Context loaded: {manager._estimate_tokens(context):,} tokens")

    # Test preference analysis
    analysis = manager.analyze_preference_evolution()
    print(f"\n📊 Preference Analysis:")
    for key, value in analysis.items():
        print(f"  {key}: {value}")

    print(f"\n🎯 Adaptive preferences system ready for integration!")