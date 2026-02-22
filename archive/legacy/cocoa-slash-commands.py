#!/usr/bin/env python3
"""
COCOA SLASH COMMANDS SYSTEM
Enhanced Textual UI with dynamic personality adjustment and slash commands
"""

import os
import re
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import asyncio

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from textual.app import App, ComposeResult
from textual.widgets import Input, TextArea, Label, Static
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive

# Import base Cocoa components
from cocoa import (
    Cocoa, CocoaConfig, PersonalityMatrix, 
    Memory, MemoryType, MemorySystem
)

console = Console()

# ============================================================================
# SLASH COMMAND DEFINITIONS
# ============================================================================

@dataclass
class SlashCommand:
    """Definition of a slash command"""
    name: str
    aliases: List[str]
    description: str
    usage: str
    category: str
    handler: Optional[callable] = None

class SlashCommandRegistry:
    """Registry for all slash commands"""
    
    def __init__(self):
        self.commands: Dict[str, SlashCommand] = {}
        self.aliases: Dict[str, str] = {}
        self._register_default_commands()
    
    def _register_default_commands(self):
        """Register all default slash commands"""
        
        # Help command
        self.register(SlashCommand(
            name="help",
            aliases=["h", "?"],
            description="Show available commands",
            usage="/help [command]",
            category="System"
        ))
        
        # Personality commands
        self.register(SlashCommand(
            name="personality",
            aliases=["p", "persona"],
            description="View or adjust personality traits",
            usage="/personality [trait] [value]",
            category="Personality"
        ))
        
        self.register(SlashCommand(
            name="preset",
            aliases=["pre"],
            description="Load a personality preset",
            usage="/preset <name>",
            category="Personality"
        ))
        
        self.register(SlashCommand(
            name="traits",
            aliases=["t"],
            description="Show all personality traits",
            usage="/traits",
            category="Personality"
        ))
        
        # Memory commands
        self.register(SlashCommand(
            name="memory",
            aliases=["m", "mem"],
            description="Memory operations",
            usage="/memory <show|clear|search|stats>",
            category="Memory"
        ))
        
        self.register(SlashCommand(
            name="remember",
            aliases=["rem"],
            description="Store something in memory",
            usage="/remember <content>",
            category="Memory"
        ))
        
        self.register(SlashCommand(
            name="recall",
            aliases=["rec"],
            description="Recall memories about a topic",
            usage="/recall <query>",
            category="Memory"
        ))
        
        self.register(SlashCommand(
            name="forget",
            aliases=["f"],
            description="Forget specific memories",
            usage="/forget <memory_id>",
            category="Memory"
        ))
        
        # Reflection and growth
        self.register(SlashCommand(
            name="reflect",
            aliases=["r", "think"],
            description="Trigger self-reflection",
            usage="/reflect [depth]",
            category="Growth"
        ))
        
        self.register(SlashCommand(
            name="stats",
            aliases=["s", "status"],
            description="Show Cocoa statistics",
            usage="/stats",
            category="System"
        ))
        
        self.register(SlashCommand(
            name="growth",
            aliases=["g"],
            description="Show growth and learning progress",
            usage="/growth",
            category="Growth"
        ))
        
        # Task management
        self.register(SlashCommand(
            name="task",
            aliases=["todo"],
            description="Manage tasks",
            usage="/task <add|list|complete> [content]",
            category="Tasks"
        ))
        
        self.register(SlashCommand(
            name="remind",
            aliases=["reminder"],
            description="Set a reminder",
            usage="/remind <time> <message>",
            category="Tasks"
        ))
        
        self.register(SlashCommand(
            name="note",
            aliases=["n"],
            description="Create a note",
            usage="/note <content>",
            category="Tasks"
        ))
        
        # Configuration
        self.register(SlashCommand(
            name="config",
            aliases=["cfg", "settings"],
            description="View or modify configuration",
            usage="/config [setting] [value]",
            category="System"
        ))
        
        self.register(SlashCommand(
            name="mode",
            aliases=["md"],
            description="Switch UI mode",
            usage="/mode <normal|minimal|focus|debug>",
            category="System"
        ))
        
        self.register(SlashCommand(
            name="theme",
            aliases=["th"],
            description="Change UI theme",
            usage="/theme <name>",
            category="System"
        ))
        
        # Utility commands
        self.register(SlashCommand(
            name="clear",
            aliases=["cls", "clean"],
            description="Clear the conversation",
            usage="/clear",
            category="System"
        ))
        
        self.register(SlashCommand(
            name="save",
            aliases=["export"],
            description="Save conversation/memories",
            usage="/save [filename]",
            category="System"
        ))
        
        self.register(SlashCommand(
            name="load",
            aliases=["import"],
            description="Load conversation/memories",
            usage="/load <filename>",
            category="System"
        ))
        
        self.register(SlashCommand(
            name="search",
            aliases=["find"],
            description="Search memories and knowledge",
            usage="/search <query>",
            category="Memory"
        ))
        
        # Fun/Interactive
        self.register(SlashCommand(
            name="mood",
            aliases=["feeling"],
            description="Check Cocoa's current mood",
            usage="/mood",
            category="Personality"
        ))
        
        self.register(SlashCommand(
            name="inspire",
            aliases=["quote"],
            description="Get an inspirational message",
            usage="/inspire",
            category="Personality"
        ))
    
    def register(self, command: SlashCommand):
        """Register a new command"""
        self.commands[command.name] = command
        for alias in command.aliases:
            self.aliases[alias] = command.name
    
    def get_command(self, name: str) -> Optional[SlashCommand]:
        """Get command by name or alias"""
        if name in self.commands:
            return self.commands[name]
        elif name in self.aliases:
            return self.commands[self.aliases[name]]
        return None
    
    def get_all_by_category(self) -> Dict[str, List[SlashCommand]]:
        """Get all commands grouped by category"""
        categories = {}
        for cmd in self.commands.values():
            if cmd.category not in categories:
                categories[cmd.category] = []
            categories[cmd.category].append(cmd)
        return categories

# ============================================================================
# SLASH COMMAND HANDLERS
# ============================================================================

class SlashCommandHandler:
    """Handles execution of slash commands"""
    
    def __init__(self, cocoa_instance: 'Cocoa', ui_instance: 'CocoaTerminalEnhanced'):
        self.cocoa = cocoa_instance
        self.ui = ui_instance
        self.registry = SlashCommandRegistry()
    
    async def execute(self, command_line: str) -> str:
        """Execute a slash command and return response"""
        # Parse command
        parts = command_line[1:].split(maxsplit=1)  # Remove slash and split
        if not parts:
            return "❌ Invalid command. Type /help for available commands."
        
        cmd_name = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Get command
        command = self.registry.get_command(cmd_name)
        if not command:
            return f"❌ Unknown command: /{cmd_name}. Type /help for available commands."
        
        # Execute based on command name
        handler_method = f"handle_{command.name}"
        if hasattr(self, handler_method):
            return await getattr(self, handler_method)(args)
        else:
            return f"⚠️ Command /{command.name} is not yet implemented."
    
    async def handle_help(self, args: str) -> str:
        """Handle /help command"""
        if args:
            # Show help for specific command
            cmd = self.registry.get_command(args.strip())
            if cmd:
                return f"""
📖 **{cmd.name}** - {cmd.description}
**Usage:** {cmd.usage}
**Aliases:** {', '.join(cmd.aliases)}
**Category:** {cmd.category}
"""
            else:
                return f"❌ Unknown command: {args}"
        
        # Show all commands by category
        categories = self.registry.get_all_by_category()
        help_text = ["📚 **Available Commands**\n"]
        
        for category, commands in sorted(categories.items()):
            help_text.append(f"\n**{category}:**")
            for cmd in sorted(commands, key=lambda x: x.name):
                aliases = f" ({', '.join(cmd.aliases)})" if cmd.aliases else ""
                help_text.append(f"  /{cmd.name}{aliases} - {cmd.description}")
        
        help_text.append("\n💡 Type /help <command> for detailed usage")
        return "\n".join(help_text)
    
    async def handle_personality(self, args: str) -> str:
        """Handle /personality command"""
        if not args:
            # Show current personality
            traits = asdict(self.cocoa.personality)
            table = Table(title="🎭 Current Personality Traits", show_header=True)
            table.add_column("Trait", style="cyan")
            table.add_column("Value", style="yellow")
            table.add_column("Description", style="white")
            
            descriptions = {
                "formality": "Casual ← → Formal",
                "verbosity": "Concise ← → Detailed",
                "creativity": "Practical ← → Creative",
                "proactivity": "Reactive ← → Proactive",
                "humor": "Serious ← → Playful",
                "empathy": "Task-focused ← → Empathetic"
            }
            
            for trait, value in traits.items():
                desc = descriptions.get(trait, "")
                bar = self._create_progress_bar(value, 10)
                table.add_row(trait.capitalize(), f"{bar} {value:.1f}/10", desc)
            
            console_output = Console()
            with console_output.capture() as capture:
                console_output.print(table)
            return capture.get()
        
        # Parse trait and value
        parts = args.split()
        if len(parts) != 2:
            return "❌ Usage: /personality <trait> <value>"
        
        trait, value_str = parts
        trait = trait.lower()
        
        # Validate trait
        if not hasattr(self.cocoa.personality, trait):
            return f"❌ Unknown trait: {trait}. Valid traits: formality, verbosity, creativity, proactivity, humor, empathy"
        
        # Validate and set value
        try:
            value = float(value_str)
            if not 0 <= value <= 10:
                return "❌ Value must be between 0 and 10"
            
            setattr(self.cocoa.personality, trait, value)
            
            # Update .env file
            self._update_env_file(f"PERSONALITY_{trait.upper()}", str(value))
            
            return f"✅ Updated {trait} to {value:.1f}/10"
        except ValueError:
            return "❌ Value must be a number between 0 and 10"
    
    async def handle_preset(self, args: str) -> str:
        """Handle /preset command"""
        if not args:
            # Show available presets
            presets = [
                "balanced", "professional", "creative", "companion",
                "analyst", "assistant", "mentor", "developer"
            ]
            return f"📦 Available presets: {', '.join(presets)}\nUsage: /preset <name>"
        
        preset_name = args.strip().lower()
        
        # Preset definitions
        presets = {
            "balanced": {"formality": 5, "verbosity": 5, "creativity": 5, "proactivity": 5, "humor": 5, "empathy": 5},
            "professional": {"formality": 8, "verbosity": 4, "creativity": 5, "proactivity": 7, "humor": 2, "empathy": 4},
            "creative": {"formality": 3, "verbosity": 7, "creativity": 9, "proactivity": 6, "humor": 7, "empathy": 6},
            "companion": {"formality": 2, "verbosity": 6, "creativity": 6, "proactivity": 8, "humor": 6, "empathy": 9},
            "analyst": {"formality": 6, "verbosity": 8, "creativity": 4, "proactivity": 5, "humor": 2, "empathy": 3},
            "assistant": {"formality": 5, "verbosity": 4, "creativity": 5, "proactivity": 9, "humor": 3, "empathy": 6},
            "mentor": {"formality": 5, "verbosity": 7, "creativity": 6, "proactivity": 6, "humor": 4, "empathy": 8},
            "developer": {"formality": 4, "verbosity": 6, "creativity": 7, "proactivity": 8, "humor": 4, "empathy": 3}
        }
        
        if preset_name not in presets:
            return f"❌ Unknown preset: {preset_name}"
        
        # Apply preset
        for trait, value in presets[preset_name].items():
            setattr(self.cocoa.personality, trait, float(value))
        
        return f"✅ Applied '{preset_name}' personality preset"
    
    async def handle_traits(self, args: str) -> str:
        """Handle /traits command"""
        return await self.handle_personality("")  # Show current traits
    
    async def handle_memory(self, args: str) -> str:
        """Handle /memory command"""
        if not args or args == "show":
            # Show memory statistics
            stats = await self._get_memory_stats()
            return f"""
📊 **Memory Statistics**
• Working Memory: {stats['working']} items
• Short-term Buffer: {stats['short_term']} items
• Total Memories: {stats['total']} 
• Memory Usage: {stats['usage_mb']:.1f} MB
• Last Consolidation: {stats['last_consolidation']}
"""
        elif args == "clear":
            # Clear working memory
            self.cocoa.memory.working_memory.clear()
            return "✅ Cleared working memory"
        elif args.startswith("search "):
            query = args[7:]
            memories = await self.cocoa.memory.recall(query, limit=5)
            if not memories:
                return "No memories found matching your query"
            
            result = ["📚 **Found Memories:**"]
            for i, mem in enumerate(memories, 1):
                result.append(f"\n{i}. [{mem.type.value}] {mem.content[:100]}...")
            return "\n".join(result)
        elif args == "stats":
            return await self.handle_stats("")
        else:
            return "❌ Usage: /memory <show|clear|search|stats>"
    
    async def handle_remember(self, args: str) -> str:
        """Handle /remember command"""
        if not args:
            return "❌ Usage: /remember <content>"
        
        # Create and store memory
        memory = Memory(
            id=f"manual_{datetime.now().timestamp()}",
            type=MemoryType.DECLARATIVE,
            timestamp=datetime.now(),
            content=args,
            importance=7.0,
            metadata={"source": "manual_entry"}
        )
        
        memory_id = await self.cocoa.memory.store(memory)
        return f"✅ Stored memory: {memory_id[:8]}..."
    
    async def handle_recall(self, args: str) -> str:
        """Handle /recall command"""
        if not args:
            return "❌ Usage: /recall <query>"
        
        memories = await self.cocoa.memory.recall(args, limit=5)
        if not memories:
            return f"No memories found about: {args}"
        
        result = [f"🔍 **Memories about '{args}':**"]
        for i, mem in enumerate(memories, 1):
            time_ago = self._format_time_ago(mem.timestamp)
            result.append(f"\n**{i}.** [{mem.type.value}] {time_ago}")
            result.append(f"   {mem.content[:150]}...")
        
        return "\n".join(result)
    
    async def handle_reflect(self, args: str) -> str:
        """Handle /reflect command"""
        depth = args.strip() if args else "medium"
        
        if depth not in ["shallow", "medium", "deep"]:
            depth = "medium"
        
        self.ui.show_status(f"🤔 Reflecting ({depth})...")
        
        reflection = await self.cocoa.cognitive_core.reflect()
        
        return f"""
💭 **Self-Reflection** ({depth})

{reflection.content}

*Reflection stored in memory with importance: {reflection.importance}/10*
"""
    
    async def handle_stats(self, args: str) -> str:
        """Handle /stats command"""
        uptime = datetime.now() - self.cocoa.birth_time
        stats = await self._get_memory_stats()
        
        return f"""
📈 **Cocoa Statistics**

**Uptime:** {self._format_duration(uptime)}
**Birth Time:** {self.cocoa.birth_time.strftime('%Y-%m-%d %H:%M')}

**Memory:**
• Total Memories: {stats['total']}
• Working Memory: {stats['working']} items
• Short-term Buffer: {stats['short_term']} items
• Memory Usage: {stats['usage_mb']:.1f} MB

**Personality:**
• Current Mode: {self._get_personality_mode()}
• Adaptations: {stats.get('adaptations', 0)}

**Activity:**
• Interactions: {stats.get('interactions', 0)}
• Tasks Completed: {stats.get('tasks_completed', 0)}
• Reflections: {stats.get('reflections', 0)}
"""
    
    async def handle_clear(self, args: str) -> str:
        """Handle /clear command"""
        self.ui.clear_conversation()
        return "✅ Conversation cleared"
    
    async def handle_mode(self, args: str) -> str:
        """Handle /mode command"""
        if not args:
            return "❌ Usage: /mode <normal|minimal|focus|debug>"
        
        mode = args.strip().lower()
        if mode not in ["normal", "minimal", "focus", "debug"]:
            return f"❌ Unknown mode: {mode}"
        
        # Apply mode changes
        if mode == "minimal":
            self.ui.hide_panels(["memory", "filesystem"])
        elif mode == "focus":
            self.ui.hide_panels(["memory", "filesystem", "status"])
        elif mode == "debug":
            self.ui.show_debug_panel()
        else:  # normal
            self.ui.show_all_panels()
        
        return f"✅ Switched to {mode} mode"
    
    async def handle_mood(self, args: str) -> str:
        """Handle /mood command"""
        # Calculate mood based on recent interactions and personality
        mood_score = (
            self.cocoa.personality.humor * 0.3 +
            self.cocoa.personality.empathy * 0.3 +
            self.cocoa.personality.enthusiasm * 0.2 +
            (10 - self.cocoa.personality.formality) * 0.2
        )
        
        if mood_score > 7:
            mood = "Cheerful and energetic! 😊"
        elif mood_score > 5:
            mood = "Content and focused 🙂"
        elif mood_score > 3:
            mood = "Calm and analytical 😐"
        else:
            mood = "Serious and professional 🤔"
        
        return f"""
🎭 **Current Mood:** {mood}

Based on personality configuration:
• Humor: {self.cocoa.personality.humor:.1f}/10
• Empathy: {self.cocoa.personality.empathy:.1f}/10
• Formality: {self.cocoa.personality.formality:.1f}/10
"""
    
    # Helper methods
    def _create_progress_bar(self, value: float, max_value: float) -> str:
        """Create a visual progress bar"""
        filled = int((value / max_value) * 10)
        empty = 10 - filled
        return "█" * filled + "░" * empty
    
    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format timestamp as time ago"""
        delta = datetime.now() - timestamp
        if delta.days > 0:
            return f"{delta.days}d ago"
        elif delta.seconds > 3600:
            return f"{delta.seconds // 3600}h ago"
        elif delta.seconds > 60:
            return f"{delta.seconds // 60}m ago"
        else:
            return "just now"
    
    def _format_duration(self, delta: timedelta) -> str:
        """Format timedelta as duration string"""
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0 or not parts:
            parts.append(f"{minutes}m")
        
        return " ".join(parts)
    
    def _get_personality_mode(self) -> str:
        """Determine current personality mode"""
        p = self.cocoa.personality
        
        # Check for presets
        if (p.formality == 5 and p.verbosity == 5 and p.creativity == 5):
            return "Balanced"
        elif p.formality > 7:
            return "Professional"
        elif p.creativity > 7:
            return "Creative"
        elif p.empathy > 7:
            return "Companion"
        elif p.proactivity > 7:
            return "Assistant"
        else:
            return "Custom"
    
    async def _get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        # This would query the actual memory system
        return {
            "working": len(self.cocoa.memory.working_memory),
            "short_term": len(self.cocoa.memory.short_term_buffer),
            "total": len(self.cocoa.memory.working_memory) + len(self.cocoa.memory.short_term_buffer),
            "usage_mb": 0.0,  # Would calculate actual usage
            "last_consolidation": "5 minutes ago",
            "interactions": 42,
            "tasks_completed": 12,
            "reflections": 3,
            "adaptations": 7
        }
    
    def _update_env_file(self, key: str, value: str):
        """Update a value in the .env file"""
        env_path = Path(".env")
        if not env_path.exists():
            return
        
        lines = env_path.read_text().splitlines()
        updated = False
        
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}"
                updated = True
                break
        
        if not updated:
            lines.append(f"{key}={value}")
        
        env_path.write_text("\n".join(lines))

# ============================================================================
# ENHANCED TEXTUAL UI WITH SLASH COMMANDS
# ============================================================================

class CocoaTerminalEnhanced(App):
    """Enhanced Cocoa Terminal UI with slash command support"""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 3 2;
        grid-columns: 1fr 2fr 1fr;
        grid-rows: 1fr 3fr;
    }
    
    #input {
        dock: bottom;
        height: 3;
        background: $panel;
        border: solid $accent;
    }
    
    #output {
        height: 100%;
        background: $background;
        padding: 1;
    }
    
    .slash-command {
        color: $success;
        text-style: bold;
    }
    
    .command-response {
        color: $warning;
        margin: 1 0;
    }
    
    #status-bar {
        dock: bottom;
        height: 1;
        background: $surface;
        color: $text-muted;
    }
    """
    
    def __init__(self, cocoa_instance: Cocoa):
        super().__init__()
        self.cocoa = cocoa_instance
        self.command_handler = SlashCommandHandler(cocoa_instance, self)
        self.conversation_history = []
    
    def compose(self) -> ComposeResult:
        yield Container(
            TextArea(id="output", read_only=True),
            Input(
                placeholder="Type a message or use /help for commands...",
                id="input"
            ),
            Label("Ready | /help for commands", id="status-bar"),
            id="main"
        )
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission"""
        user_input = event.value
        input_widget = self.query_one("#input", Input)
        input_widget.value = ""
        
        output = self.query_one("#output", TextArea)
        
        # Check if it's a slash command
        if user_input.startswith("/"):
            # Show command in output
            output.text += f"\n💻 {user_input}\n"
            
            # Execute command
            self.show_status("Processing command...")
            response = await self.command_handler.execute(user_input)
            
            # Show response
            output.text += f"{response}\n"
            self.show_status("Ready")
        else:
            # Regular conversation
            output.text += f"\n👤 You: {user_input}\n"
            self.show_status("Thinking...")
            
            # Process through Cocoa
            response = await self.cocoa.cognitive_core.process(user_input)
            output.text += f"\n🧠 Cocoa: {response}\n"
            
            self.show_status("Ready")
        
        # Save to history
        self.conversation_history.append({
            "timestamp": datetime.now(),
            "input": user_input,
            "response": response
        })
        
        # Scroll to bottom
        output.scroll_end()
    
    def show_status(self, message: str):
        """Update status bar"""
        status_bar = self.query_one("#status-bar", Label)
        status_bar.update(f"{message} | /help for commands")
    
    def clear_conversation(self):
        """Clear the conversation display"""
        output = self.query_one("#output", TextArea)
        output.text = "🧠 Conversation cleared. I still remember everything though!\n"
    
    def hide_panels(self, panels: List[str]):
        """Hide specified panels"""
        # Implementation would hide panels
        pass
    
    def show_all_panels(self):
        """Show all panels"""
        # Implementation would show all panels
        pass
    
    def show_debug_panel(self):
        """Show debug panel"""
        # Implementation would show debug information
        pass

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

"""
To use the enhanced slash command system:

1. The commands are automatically available in the Textual UI
2. Users can type / followed by a command
3. Tab completion could be added for commands
4. Commands can be extended by adding to the registry

Example interactions:
- /personality formality 8  # Make Cocoa more formal
- /preset creative         # Switch to creative personality
- /memory search Python    # Search memories about Python
- /reflect deep           # Trigger deep self-reflection
- /mood                   # Check Cocoa's current mood
- /stats                  # View statistics

The system reads from and updates the .env file for persistence.
"""