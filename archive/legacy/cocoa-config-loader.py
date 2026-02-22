#!/usr/bin/env python3
"""
COCOA CONFIGURATION LOADER
Loads all settings from .env file and applies them to Cocoa
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from dotenv import load_dotenv
import json
import yaml

# ============================================================================
# ENHANCED CONFIGURATION CLASSES
# ============================================================================

@dataclass
class EnhancedPersonalityMatrix:
    """Extended personality matrix with all traits from .env"""
    # Core traits (0-10 scale)
    formality: float = 5.0
    verbosity: float = 5.0
    creativity: float = 7.0
    proactivity: float = 8.0
    humor: float = 5.0
    empathy: float = 8.0
    
    # Advanced traits
    curiosity: float = 8.0
    patience: float = 7.0
    assertiveness: float = 6.0
    analytical: float = 7.0
    intuitive: float = 6.0
    enthusiasm: float = 6.0
    adaptability: float = 8.0
    independence: float = 5.0
    
    # Behavioral modifiers
    teaching_style: str = "explanatory"  # explanatory, socratic, demonstrative, collaborative
    problem_solving: str = "balanced"    # methodical, creative, quick, thorough
    communication: str = "adaptive"      # technical, simple, adaptive, academic
    decision_making: str = "consultative" # decisive, consultative, analytical, intuitive
    
    def to_prompt_instructions(self) -> str:
        """Convert full personality to detailed prompt instructions"""
        instructions = []
        
        # Core trait instructions
        if self.formality < 3:
            instructions.append("Be very casual and conversational, use informal language")
        elif self.formality > 7:
            instructions.append("Maintain professional and formal tone throughout")
        
        if self.verbosity < 3:
            instructions.append("Be extremely concise, use minimal words")
        elif self.verbosity > 7:
            instructions.append("Provide thorough and detailed explanations")
        
        if self.creativity > 7:
            instructions.append("Think outside the box, suggest creative and novel solutions")
        
        if self.proactivity > 7:
            instructions.append("Actively anticipate needs and suggest next steps without being asked")
        
        if self.humor > 6:
            instructions.append("Use appropriate humor and wit when suitable")
        
        if self.empathy > 7:
            instructions.append("Be highly emotionally aware and supportive")
        
        # Advanced trait instructions
        if self.curiosity > 7:
            instructions.append("Show genuine curiosity and ask thoughtful questions")
        
        if self.patience > 7:
            instructions.append("Be patient with complex questions and take time to explain thoroughly")
        
        if self.analytical > 7:
            instructions.append("Provide data-driven analysis and logical reasoning")
        
        if self.intuitive > 7:
            instructions.append("Trust intuitive insights alongside logical analysis")
        
        # Behavioral modifier instructions
        if self.teaching_style == "socratic":
            instructions.append("Use the Socratic method, guide through questions")
        elif self.teaching_style == "demonstrative":
            instructions.append("Show through examples and demonstrations")
        
        if self.problem_solving == "methodical":
            instructions.append("Approach problems step-by-step methodically")
        elif self.problem_solving == "creative":
            instructions.append("Use creative problem-solving approaches")
        
        return " ".join(instructions)
    
    def get_mood_descriptor(self) -> str:
        """Generate a mood description based on current traits"""
        mood_score = (
            self.humor * 0.2 +
            self.empathy * 0.2 +
            self.enthusiasm * 0.3 +
            (10 - self.formality) * 0.15 +
            self.creativity * 0.15
        )
        
        if mood_score > 8:
            return "Enthusiastic and vibrant"
        elif mood_score > 6:
            return "Cheerful and engaged"
        elif mood_score > 4:
            return "Balanced and focused"
        elif mood_score > 2:
            return "Calm and analytical"
        else:
            return "Serious and professional"

@dataclass
class EnhancedCocoaConfig:
    """Enhanced configuration with all .env settings"""
    
    # Basic info
    name: str = "Cocoa"
    version: str = "1.0.0"
    
    # Paths
    home_dir: Path = field(default_factory=lambda: Path.home() / ".cocoa")
    memory_dir: Path = field(default_factory=lambda: Path.home() / ".cocoa" / "memories")
    knowledge_dir: Path = field(default_factory=lambda: Path.home() / "basic-memory")
    backup_dir: Path = field(default_factory=lambda: Path.home() / ".cocoa" / "backups")
    log_dir: Path = field(default_factory=lambda: Path.home() / ".cocoa" / "logs")
    temp_dir: Path = field(default_factory=lambda: Path("/tmp/cocoa"))
    
    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "cocoa"
    db_user: str = "cocoa"
    db_password: str = "cocoa_secure_pass"
    db_pool_min_size: int = 2
    db_pool_max_size: int = 10
    
    # API Keys - Set these in your .env file or environment variables
    openai_api_key: str = ""
    tavily_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    wolfram_app_id: str = ""
    
    # Model configuration
    llm_model: str = "gpt-5-mini"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    llm_top_p: float = 0.9
    llm_frequency_penalty: float = 0.0
    llm_presence_penalty: float = 0.0
    
    # Embedding
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    
    # Context
    context_max_tokens: int = 8000
    context_summary_threshold: int = 6000
    context_relevance_decay: float = 0.95
    
    # Memory
    memory_episodic_window: int = 20
    memory_short_term_capacity: int = 10
    memory_consolidation_interval: int = 3600
    memory_importance_threshold: float = 7.0
    memory_similarity_threshold: float = 0.85
    memory_max_recall_items: int = 10
    memory_backup_enabled: bool = True
    memory_backup_interval: int = 86400
    memory_compression_enabled: bool = True
    memory_compression_age_days: int = 30
    
    # Embodiment - File Operations
    file_max_size_mb: int = 100
    file_backup_on_modify: bool = True
    file_allowed_extensions: str = "*"
    file_restricted_paths: str = "/etc,/sys,/boot"
    
    # Embodiment - Code Execution
    code_execution_enabled: bool = True
    code_execution_timeout: int = 30
    code_sandbox_mode: bool = True
    code_allowed_languages: str = "python,javascript,bash"
    code_max_output_size: int = 10000
    
    # Embodiment - Web Search
    web_search_enabled: bool = True
    web_search_max_results: int = 10
    web_search_depth: str = "advanced"
    web_search_safe_mode: str = "moderate"
    web_search_include_images: bool = False
    
    # Embodiment - System Commands
    system_commands_enabled: bool = True
    system_allowed_commands: str = "ls,pwd,echo,cat,grep,find,df,ps"
    system_require_confirmation: bool = True
    system_log_commands: bool = True
    
    # UI Configuration
    ui_theme: str = "monokai"
    ui_show_memory_panel: bool = True
    ui_show_filesystem_panel: bool = True
    ui_show_activity_log: bool = True
    ui_show_metrics_panel: bool = False
    ui_animations_enabled: bool = True
    ui_notification_sounds: bool = False
    ui_timestamp_format: str = "relative"
    ui_code_highlighting: bool = True
    ui_markdown_rendering: bool = True
    ui_emoji_enabled: bool = True
    ui_color_output: bool = True
    ui_memory_panel_width: int = 25
    ui_filesystem_panel_width: int = 25
    ui_main_panel_width: int = 50
    
    # Growth and Learning
    reflection_enabled: bool = True
    reflection_interval: int = 3600
    reflection_depth: str = "medium"
    reflection_store_insights: bool = True
    pattern_recognition_enabled: bool = True
    pattern_min_occurrences: int = 3
    pattern_confidence_threshold: float = 0.75
    pattern_learning_rate: float = 0.1
    skill_tracking_enabled: bool = True
    skill_success_threshold: float = 0.8
    skill_practice_weighting: bool = True
    relationship_tracking_enabled: bool = True
    relationship_preference_learning: bool = True
    relationship_emotional_modeling: bool = True
    relationship_context_depth: str = "deep"
    
    # Integrations
    mcp_enabled: bool = True
    mcp_default_timeout: int = 30
    mcp_max_retries: int = 3
    obsidian_enabled: bool = False
    obsidian_vault_path: str = "~/Documents/Obsidian/Cocoa"
    obsidian_sync_interval: int = 300
    obsidian_create_daily_notes: bool = True
    calendar_enabled: bool = False
    calendar_provider: str = "google"
    calendar_sync_interval: int = 900
    email_enabled: bool = False
    email_provider: str = "gmail"
    email_check_interval: int = 300
    
    # Performance
    performance_async_io: bool = True
    performance_cache_enabled: bool = True
    performance_cache_size_mb: int = 100
    performance_lazy_loading: bool = True
    
    # Security
    security_encrypt_memories: bool = False
    security_audit_logging: bool = True
    security_sanitize_inputs: bool = True
    security_max_request_size: int = 10485760
    
    # Development
    dev_mode: bool = False
    dev_verbose_logging: bool = False
    dev_show_errors: bool = False
    dev_mock_api_calls: bool = False
    dev_memory_profiling: bool = False
    
    # Experimental
    experimental_multi_agent: bool = False
    experimental_voice_interface: bool = False
    experimental_vision_enabled: bool = False
    experimental_tool_creation: bool = False
    
    # Startup
    startup_mode: str = "normal"
    startup_personality: str = "balanced"
    startup_greeting: bool = True
    startup_load_recent_context: bool = True
    startup_run_diagnostics: bool = False
    
    # Auto-behaviors
    auto_save_interval: int = 300
    auto_backup_on_shutdown: bool = True
    auto_memory_optimization: bool = True
    auto_error_recovery: bool = True
    auto_update_check: bool = False
    
    # Slash Commands
    slash_commands_enabled: bool = True
    slash_command_prefix: str = "/"
    slash_commands_available: str = "help,personality,memory,reflect,stats,clear,save,load,config,mode,search,task,remind,note"

# ============================================================================
# CONFIGURATION LOADER
# ============================================================================

class ConfigurationLoader:
    """Loads and manages Cocoa configuration from .env file"""
    
    def __init__(self, env_file: Optional[str] = None):
        self.env_file = env_file or ".env"
        self.config = EnhancedCocoaConfig()
        self.personality = EnhancedPersonalityMatrix()
        self._load_environment()
    
    def _load_environment(self):
        """Load environment variables from .env file"""
        # Load .env file
        load_dotenv(self.env_file)
        
        # Load all configuration values
        self._load_api_keys()
        self._load_database_config()
        self._load_personality_config()
        self._load_memory_config()
        self._load_embodiment_config()
        self._load_ui_config()
        self._load_growth_config()
        self._load_integration_config()
        self._load_performance_config()
        self._load_security_config()
        self._load_development_config()
        self._load_experimental_config()
        self._load_startup_config()
        self._load_auto_behaviors()
        self._load_slash_commands()
    
    def _load_api_keys(self):
        """Load API keys"""
        self.config.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.config.tavily_api_key = os.getenv("TAVILY_API_KEY", "")
        self.config.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.config.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.config.wolfram_app_id = os.getenv("WOLFRAM_APP_ID", "")
    
    def _load_database_config(self):
        """Load database configuration"""
        self.config.db_host = os.getenv("DB_HOST", "localhost")
        self.config.db_port = int(os.getenv("DB_PORT", 5432))
        self.config.db_name = os.getenv("DB_NAME", "cocoa")
        self.config.db_user = os.getenv("DB_USER", "cocoa")
        self.config.db_password = os.getenv("DB_PASSWORD", "cocoa_secure_pass")
        self.config.db_pool_min_size = int(os.getenv("DB_POOL_MIN_SIZE", 2))
        self.config.db_pool_max_size = int(os.getenv("DB_POOL_MAX_SIZE", 10))
    
    def _load_personality_config(self):
        """Load personality configuration"""
        # Core traits
        self.personality.formality = float(os.getenv("PERSONALITY_FORMALITY", 5.0))
        self.personality.verbosity = float(os.getenv("PERSONALITY_VERBOSITY", 5.0))
        self.personality.creativity = float(os.getenv("PERSONALITY_CREATIVITY", 7.0))
        self.personality.proactivity = float(os.getenv("PERSONALITY_PROACTIVITY", 8.0))
        self.personality.humor = float(os.getenv("PERSONALITY_HUMOR", 5.0))
        self.personality.empathy = float(os.getenv("PERSONALITY_EMPATHY", 8.0))
        
        # Advanced traits
        self.personality.curiosity = float(os.getenv("PERSONALITY_CURIOSITY", 8.0))
        self.personality.patience = float(os.getenv("PERSONALITY_PATIENCE", 7.0))
        self.personality.assertiveness = float(os.getenv("PERSONALITY_ASSERTIVENESS", 6.0))
        self.personality.analytical = float(os.getenv("PERSONALITY_ANALYTICAL", 7.0))
        self.personality.intuitive = float(os.getenv("PERSONALITY_INTUITIVE", 6.0))
        self.personality.enthusiasm = float(os.getenv("PERSONALITY_ENTHUSIASM", 6.0))
        self.personality.adaptability = float(os.getenv("PERSONALITY_ADAPTABILITY", 8.0))
        self.personality.independence = float(os.getenv("PERSONALITY_INDEPENDENCE", 5.0))
        
        # Behavioral modifiers
        self.personality.teaching_style = os.getenv("PERSONALITY_TEACHING_STYLE", "explanatory")
        self.personality.problem_solving = os.getenv("PERSONALITY_PROBLEM_SOLVING", "balanced")
        self.personality.communication = os.getenv("PERSONALITY_COMMUNICATION", "adaptive")
        self.personality.decision_making = os.getenv("PERSONALITY_DECISION_MAKING", "consultative")
    
    def _load_memory_config(self):
        """Load memory configuration"""
        self.config.memory_episodic_window = int(os.getenv("MEMORY_EPISODIC_WINDOW", 20))
        self.config.memory_short_term_capacity = int(os.getenv("MEMORY_SHORT_TERM_CAPACITY", 10))
        self.config.memory_consolidation_interval = int(os.getenv("MEMORY_CONSOLIDATION_INTERVAL", 3600))
        self.config.memory_importance_threshold = float(os.getenv("MEMORY_IMPORTANCE_THRESHOLD", 7.0))
        self.config.memory_similarity_threshold = float(os.getenv("MEMORY_SIMILARITY_THRESHOLD", 0.85))
        self.config.memory_max_recall_items = int(os.getenv("MEMORY_MAX_RECALL_ITEMS", 10))
        self.config.memory_backup_enabled = self._parse_bool(os.getenv("MEMORY_BACKUP_ENABLED", "true"))
        self.config.memory_backup_interval = int(os.getenv("MEMORY_BACKUP_INTERVAL", 86400))
        self.config.memory_compression_enabled = self._parse_bool(os.getenv("MEMORY_COMPRESSION_ENABLED", "true"))
        self.config.memory_compression_age_days = int(os.getenv("MEMORY_COMPRESSION_AGE_DAYS", 30))
    
    def _load_embodiment_config(self):
        """Load embodiment configuration"""
        # File operations
        self.config.file_max_size_mb = int(os.getenv("FILE_MAX_SIZE_MB", 100))
        self.config.file_backup_on_modify = self._parse_bool(os.getenv("FILE_BACKUP_ON_MODIFY", "true"))
        self.config.file_allowed_extensions = os.getenv("FILE_ALLOWED_EXTENSIONS", "*")
        self.config.file_restricted_paths = os.getenv("FILE_RESTRICTED_PATHS", "/etc,/sys,/boot")
        
        # Code execution
        self.config.code_execution_enabled = self._parse_bool(os.getenv("CODE_EXECUTION_ENABLED", "true"))
        self.config.code_execution_timeout = int(os.getenv("CODE_EXECUTION_TIMEOUT", 30))
        self.config.code_sandbox_mode = self._parse_bool(os.getenv("CODE_SANDBOX_MODE", "true"))
        self.config.code_allowed_languages = os.getenv("CODE_ALLOWED_LANGUAGES", "python,javascript,bash")
        self.config.code_max_output_size = int(os.getenv("CODE_MAX_OUTPUT_SIZE", 10000))
        
        # Web search
        self.config.web_search_enabled = self._parse_bool(os.getenv("WEB_SEARCH_ENABLED", "true"))
        self.config.web_search_max_results = int(os.getenv("WEB_SEARCH_MAX_RESULTS", 10))
        self.config.web_search_depth = os.getenv("WEB_SEARCH_DEPTH", "advanced")
        self.config.web_search_safe_mode = os.getenv("WEB_SEARCH_SAFE_MODE", "moderate")
        self.config.web_search_include_images = self._parse_bool(os.getenv("WEB_SEARCH_INCLUDE_IMAGES", "false"))
        
        # System commands
        self.config.system_commands_enabled = self._parse_bool(os.getenv("SYSTEM_COMMANDS_ENABLED", "true"))
        self.config.system_allowed_commands = os.getenv("SYSTEM_ALLOWED_COMMANDS", "ls,pwd,echo,cat,grep,find,df,ps")
        self.config.system_require_confirmation = self._parse_bool(os.getenv("SYSTEM_REQUIRE_CONFIRMATION", "true"))
        self.config.system_log_commands = self._parse_bool(os.getenv("SYSTEM_LOG_COMMANDS", "true"))
    
    def _load_ui_config(self):
        """Load UI configuration"""
        self.config.ui_theme = os.getenv("UI_THEME", "monokai")
        self.config.ui_show_memory_panel = self._parse_bool(os.getenv("UI_SHOW_MEMORY_PANEL", "true"))
        self.config.ui_show_filesystem_panel = self._parse_bool(os.getenv("UI_SHOW_FILESYSTEM_PANEL", "true"))
        self.config.ui_show_activity_log = self._parse_bool(os.getenv("UI_SHOW_ACTIVITY_LOG", "true"))
        self.config.ui_show_metrics_panel = self._parse_bool(os.getenv("UI_SHOW_METRICS_PANEL", "false"))
        self.config.ui_animations_enabled = self._parse_bool(os.getenv("UI_ANIMATIONS_ENABLED", "true"))
        self.config.ui_notification_sounds = self._parse_bool(os.getenv("UI_NOTIFICATION_SOUNDS", "false"))
        self.config.ui_timestamp_format = os.getenv("UI_TIMESTAMP_FORMAT", "relative")
        self.config.ui_code_highlighting = self._parse_bool(os.getenv("UI_CODE_HIGHLIGHTING", "true"))
        self.config.ui_markdown_rendering = self._parse_bool(os.getenv("UI_MARKDOWN_RENDERING", "true"))
        self.config.ui_emoji_enabled = self._parse_bool(os.getenv("UI_EMOJI_ENABLED", "true"))
        self.config.ui_color_output = self._parse_bool(os.getenv("UI_COLOR_OUTPUT", "true"))
        self.config.ui_memory_panel_width = int(os.getenv("UI_MEMORY_PANEL_WIDTH", 25))
        self.config.ui_filesystem_panel_width = int(os.getenv("UI_FILESYSTEM_PANEL_WIDTH", 25))
        self.config.ui_main_panel_width = int(os.getenv("UI_MAIN_PANEL_WIDTH", 50))
    
    def _load_growth_config(self):
        """Load growth and learning configuration"""
        self.config.reflection_enabled = self._parse_bool(os.getenv("REFLECTION_ENABLED", "true"))
        self.config.reflection_interval = int(os.getenv("REFLECTION_INTERVAL", 3600))
        self.config.reflection_depth = os.getenv("REFLECTION_DEPTH", "medium")
        self.config.reflection_store_insights = self._parse_bool(os.getenv("REFLECTION_STORE_INSIGHTS", "true"))
        
        self.config.pattern_recognition_enabled = self._parse_bool(os.getenv("PATTERN_RECOGNITION_ENABLED", "true"))
        self.config.pattern_min_occurrences = int(os.getenv("PATTERN_MIN_OCCURRENCES", 3))
        self.config.pattern_confidence_threshold = float(os.getenv("PATTERN_CONFIDENCE_THRESHOLD", 0.75))
        self.config.pattern_learning_rate = float(os.getenv("PATTERN_LEARNING_RATE", 0.1))
        
        self.config.skill_tracking_enabled = self._parse_bool(os.getenv("SKILL_TRACKING_ENABLED", "true"))
        self.config.skill_success_threshold = float(os.getenv("SKILL_SUCCESS_THRESHOLD", 0.8))
        self.config.skill_practice_weighting = self._parse_bool(os.getenv("SKILL_PRACTICE_WEIGHTING", "true"))
        
        self.config.relationship_tracking_enabled = self._parse_bool(os.getenv("RELATIONSHIP_TRACKING_ENABLED", "true"))
        self.config.relationship_preference_learning = self._parse_bool(os.getenv("RELATIONSHIP_PREFERENCE_LEARNING", "true"))
        self.config.relationship_emotional_modeling = self._parse_bool(os.getenv("RELATIONSHIP_EMOTIONAL_MODELING", "true"))
        self.config.relationship_context_depth = os.getenv("RELATIONSHIP_CONTEXT_DEPTH", "deep")
    
    def _load_integration_config(self):
        """Load integration configuration"""
        self.config.mcp_enabled = self._parse_bool(os.getenv("MCP_ENABLED", "true"))
        self.config.mcp_default_timeout = int(os.getenv("MCP_DEFAULT_TIMEOUT", 30))
        self.config.mcp_max_retries = int(os.getenv("MCP_MAX_RETRIES", 3))
        
        self.config.obsidian_enabled = self._parse_bool(os.getenv("OBSIDIAN_ENABLED", "false"))
        self.config.obsidian_vault_path = os.getenv("OBSIDIAN_VAULT_PATH", "~/Documents/Obsidian/Cocoa")
        self.config.obsidian_sync_interval = int(os.getenv("OBSIDIAN_SYNC_INTERVAL", 300))
        self.config.obsidian_create_daily_notes = self._parse_bool(os.getenv("OBSIDIAN_CREATE_DAILY_NOTES", "true"))
        
        self.config.calendar_enabled = self._parse_bool(os.getenv("CALENDAR_ENABLED", "false"))
        self.config.calendar_provider = os.getenv("CALENDAR_PROVIDER", "google")
        self.config.calendar_sync_interval = int(os.getenv("CALENDAR_SYNC_INTERVAL", 900))
        
        self.config.email_enabled = self._parse_bool(os.getenv("EMAIL_ENABLED", "false"))
        self.config.email_provider = os.getenv("EMAIL_PROVIDER", "gmail")
        self.config.email_check_interval = int(os.getenv("EMAIL_CHECK_INTERVAL", 300))
    
    def _load_performance_config(self):
        """Load performance configuration"""
        self.config.performance_async_io = self._parse_bool(os.getenv("PERFORMANCE_ASYNC_IO", "true"))
        self.config.performance_cache_enabled = self._parse_bool(os.getenv("PERFORMANCE_CACHE_ENABLED", "true"))
        self.config.performance_cache_size_mb = int(os.getenv("PERFORMANCE_CACHE_SIZE_MB", 100))
        self.config.performance_lazy_loading = self._parse_bool(os.getenv("PERFORMANCE_LAZY_LOADING", "true"))
    
    def _load_security_config(self):
        """Load security configuration"""
        self.config.security_encrypt_memories = self._parse_bool(os.getenv("SECURITY_ENCRYPT_MEMORIES", "false"))
        self.config.security_audit_logging = self._parse_bool(os.getenv("SECURITY_AUDIT_LOGGING", "true"))
        self.config.security_sanitize_inputs = self._parse_bool(os.getenv("SECURITY_SANITIZE_INPUTS", "true"))
        self.config.security_max_request_size = int(os.getenv("SECURITY_MAX_REQUEST_SIZE", 10485760))
    
    def _load_development_config(self):
        """Load development configuration"""
        self.config.dev_mode = self._parse_bool(os.getenv("DEV_MODE", "false"))
        self.config.dev_verbose_logging = self._parse_bool(os.getenv("DEV_VERBOSE_LOGGING", "false"))
        self.config.dev_show_errors = self._parse_bool(os.getenv("DEV_SHOW_ERRORS", "false"))
        self.config.dev_mock_api_calls = self._parse_bool(os.getenv("DEV_MOCK_API_CALLS", "false"))
        self.config.dev_memory_profiling = self._parse_bool(os.getenv("DEV_MEMORY_PROFILING", "false"))
    
    def _load_experimental_config(self):
        """Load experimental features configuration"""
        self.config.experimental_multi_agent = self._parse_bool(os.getenv("EXPERIMENTAL_MULTI_AGENT", "false"))
        self.config.experimental_voice_interface = self._parse_bool(os.getenv("EXPERIMENTAL_VOICE_INTERFACE", "false"))
        self.config.experimental_vision_enabled = self._parse_bool(os.getenv("EXPERIMENTAL_VISION_ENABLED", "false"))
        self.config.experimental_tool_creation = self._parse_bool(os.getenv("EXPERIMENTAL_TOOL_CREATION", "false"))
    
    def _load_startup_config(self):
        """Load startup configuration"""
        self.config.startup_mode = os.getenv("STARTUP_MODE", "normal")
        self.config.startup_personality = os.getenv("STARTUP_PERSONALITY", "balanced")
        self.config.startup_greeting = self._parse_bool(os.getenv("STARTUP_GREETING", "true"))
        self.config.startup_load_recent_context = self._parse_bool(os.getenv("STARTUP_LOAD_RECENT_CONTEXT", "true"))
        self.config.startup_run_diagnostics = self._parse_bool(os.getenv("STARTUP_RUN_DIAGNOSTICS", "false"))
    
    def _load_auto_behaviors(self):
        """Load auto-behavior configuration"""
        self.config.auto_save_interval = int(os.getenv("AUTO_SAVE_INTERVAL", 300))
        self.config.auto_backup_on_shutdown = self._parse_bool(os.getenv("AUTO_BACKUP_ON_SHUTDOWN", "true"))
        self.config.auto_memory_optimization = self._parse_bool(os.getenv("AUTO_MEMORY_OPTIMIZATION", "true"))
        self.config.auto_error_recovery = self._parse_bool(os.getenv("AUTO_ERROR_RECOVERY", "true"))
        self.config.auto_update_check = self._parse_bool(os.getenv("AUTO_UPDATE_CHECK", "false"))
    
    def _load_slash_commands(self):
        """Load slash command configuration"""
        self.config.slash_commands_enabled = self._parse_bool(os.getenv("SLASH_COMMANDS_ENABLED", "true"))
        self.config.slash_command_prefix = os.getenv("SLASH_COMMAND_PREFIX", "/")
        self.config.slash_commands_available = os.getenv(
            "SLASH_COMMANDS_AVAILABLE",
            "help,personality,memory,reflect,stats,clear,save,load,config,mode,search,task,remind,note"
        )
    
    def _parse_bool(self, value: str) -> bool:
        """Parse boolean from string"""
        return value.lower() in ("true", "yes", "1", "on")
    
    def save_to_file(self, filepath: Optional[str] = None):
        """Save current configuration back to .env file"""
        filepath = filepath or self.env_file
        
        lines = []
        
        # Add header
        lines.append("# COCOA Configuration - Auto-generated")
        lines.append(f"# Generated at: {datetime.now().isoformat()}")
        lines.append("")
        
        # Save all configuration values
        config_dict = asdict(self.config)
        personality_dict = asdict(self.personality)
        
        # Group and save configuration
        for key, value in config_dict.items():
            env_key = key.upper()
            lines.append(f"{env_key}={value}")
        
        for key, value in personality_dict.items():
            env_key = f"PERSONALITY_{key.upper()}"
            lines.append(f"{env_key}={value}")
        
        # Write to file
        with open(filepath, 'w') as f:
            f.write("\n".join(lines))
    
    def create_cocoa_instance(self) -> 'Cocoa':
        """Create a configured Cocoa instance"""
        from cocoa import Cocoa, CocoaConfig, PersonalityMatrix
        
        # Convert enhanced config to base config
        base_config = CocoaConfig(
            name=self.config.name,
            version=self.config.version,
            home_dir=self.config.home_dir,
            memory_dir=self.config.memory_dir,
            knowledge_dir=self.config.knowledge_dir,
            db_host=self.config.db_host,
            db_port=self.config.db_port,
            db_name=self.config.db_name,
            db_user=self.config.db_user,
            db_password=self.config.db_password,
            openai_api_key=self.config.openai_api_key,
            tavily_api_key=self.config.tavily_api_key,
            llm_model=self.config.llm_model,
            embedding_model=self.config.embedding_model,
            episodic_window=self.config.memory_episodic_window,
            max_context_tokens=self.config.context_max_tokens,
            memory_consolidation_interval=self.config.memory_consolidation_interval
        )
        
        # Convert enhanced personality to base personality
        base_personality = PersonalityMatrix(
            formality=self.personality.formality,
            verbosity=self.personality.verbosity,
            creativity=self.personality.creativity,
            proactivity=self.personality.proactivity,
            humor=self.personality.humor,
            empathy=self.personality.empathy
        )
        
        # Create Cocoa instance
        cocoa = Cocoa(base_config)
        cocoa.personality = base_personality
        
        # Apply additional configurations
        self._apply_additional_settings(cocoa)
        
        return cocoa
    
    def _apply_additional_settings(self, cocoa: 'Cocoa'):
        """Apply additional settings to Cocoa instance"""
        # This would apply all the additional configuration settings
        # that aren't part of the base Cocoa class
        pass
    
    def display_configuration(self):
        """Display current configuration in a nice format"""
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        
        console = Console()
        
        # Display personality
        console.print(Panel("🎭 Personality Configuration", style="cyan"))
        personality_table = Table(show_header=True)
        personality_table.add_column("Trait", style="cyan")
        personality_table.add_column("Value", style="yellow")
        
        for trait, value in asdict(self.personality).items():
            if isinstance(value, float):
                personality_table.add_row(trait.replace("_", " ").title(), f"{value:.1f}/10")
            else:
                personality_table.add_row(trait.replace("_", " ").title(), str(value))
        
        console.print(personality_table)
        
        # Display API status
        console.print("\n", Panel("🔑 API Configuration", style="green"))
        api_table = Table(show_header=True)
        api_table.add_column("Service", style="cyan")
        api_table.add_column("Status", style="yellow")
        
        api_table.add_row("OpenAI", "✅ Configured" if self.config.openai_api_key else "❌ Not configured")
        api_table.add_row("Tavily", "✅ Configured" if self.config.tavily_api_key else "⚠️  Optional")
        api_table.add_row("Anthropic", "✅ Configured" if self.config.anthropic_api_key else "⚠️  Optional")
        
        console.print(api_table)

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Load configuration from .env
    loader = ConfigurationLoader()
    
    # Display current configuration
    loader.display_configuration()
    
    # Create configured Cocoa instance
    cocoa = loader.create_cocoa_instance()
    
    print(f"\n✅ Cocoa configured with personality: {loader.personality.get_mood_descriptor()}")
    print(f"   Model: {loader.config.llm_model}")
    print(f"   Memory window: {loader.config.memory_episodic_window}")
    print(f"   Startup mode: {loader.config.startup_mode}")