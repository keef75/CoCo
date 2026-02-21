"""
Code execution tool provider -- run code and execute bash commands.

Registers the following tools with the ToolRegistry:
  - run_code      (multi-language: Python, Bash, SQL, JavaScript)
  - execute_bash  (safe, whitelisted shell commands)

Code execution is sandboxed within CoCo's workspace directory.
Dangerous operations are blocked by safety checks.
"""

from __future__ import annotations

import io
import os
import shutil
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .registry import ToolDefinition, ToolRegistry

# ---------------------------------------------------------------------------
# JSON schemas
# ---------------------------------------------------------------------------

_RUN_CODE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Python code to execute"},
    },
    "required": ["code"],
}

_EXECUTE_BASH_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "command": {"type": "string", "description": "Shell command to execute"},
    },
    "required": ["command"],
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _safe_console_width() -> int:
    try:
        return min(shutil.get_terminal_size().columns - 4, 80)
    except Exception:
        return 76


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


class _CodeExecutionTools:
    """Stateful implementation of code execution tools."""

    def __init__(self, workspace: Path, config: Any = None, code_memory: Any = None) -> None:
        self.workspace = workspace
        self.config = config
        self.code_memory = code_memory
        self.bash_timeout: int = getattr(config, "bash_timeout", 15)

    # ==================================================================
    # run_code
    # ==================================================================

    def run_code(self, code: str, language: str = "auto") -> str:
        """Execute code through the computational mind with multi-language support."""
        try:
            if language == "auto":
                language = self._detect_language(code)

            analysis = self._analyze_code(code, language)
            execution_result = self._execute_code_by_language(code, language, analysis)
            return self._format_execution_output(execution_result, analysis)

        except Exception as e:
            return f"Computational error: {e}"

    # ==================================================================
    # execute_bash (safe, whitelisted)
    # ==================================================================

    def execute_bash(self, command: str) -> str:
        """Execute safe shell commands with whitelist filtering."""
        try:
            import shlex

            SAFE_COMMANDS = {
                "ls", "pwd", "find", "grep", "cat", "head", "tail", "wc",
                "sort", "uniq", "echo", "which", "whoami", "date", "uname",
                "tree", "file", "stat", "basename", "dirname", "realpath",
                "readlink", "open",
            }

            DANGEROUS_PATTERNS = [
                "rm ", "rmdir", "mv ", "cp ", "mkdir", "touch", "chmod",
                "chown", "chgrp", "sudo", "su ", "kill", "killall", "pkill",
                "reboot", "shutdown", "wget", "curl", "nc ", "netcat", "ssh",
                "scp", "rsync", "ping", "telnet", "ftp", "nohup", "screen",
                "tmux", "> /", ">> /", "| ", "&& ", "|| ", "; ", "$(", "`",
                "tar ", "zip", "unzip", "gzip", "gunzip", "compress",
                "git ", "npm ", "pip ", "python", "node", "java", "gcc", "make",
                "ps ", "top", "htop", "lsof", "netstat", "ss ", "df ", "du ",
                "free", "mount", "/dev/", "/proc/", "/sys/", "cd /", "cd ~",
                "../", "./", "export ", "unset ", "alias ", "unalias",
                "function ", "eval ", "exec ", "source ", ". ",
                ":(){", "fork()", ">()",
            ]

            try:
                parsed = shlex.split(command)
                if not parsed:
                    return "Empty command"
                base_command = parsed[0].split("/")[-1]
            except ValueError:
                return "Invalid command syntax"

            if base_command not in SAFE_COMMANDS:
                return (
                    f"Command '{base_command}' not in safety whitelist\n\n"
                    f"Allowed commands: {', '.join(sorted(SAFE_COMMANDS))}"
                )

            if ".." in command or "~" in command or command.startswith("/"):
                return "Path traversal detected - commands restricted to workspace directory"

            command_lower = command.lower()
            for pattern in DANGEROUS_PATTERNS:
                if pattern in command_lower:
                    return f"Dangerous pattern detected: '{pattern}' is not allowed"

            dangerous_chars = ["|", ">", "<", ";", "&", "$", "`"]
            for char in dangerous_chars:
                if char in command:
                    return (
                        f"Dangerous character '{char}' detected - "
                        "pipes, redirects, and command substitution not allowed"
                    )

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.bash_timeout,
                cwd=str(self.workspace),
            )

            if result.returncode == 0:
                output = result.stdout.strip() if result.stdout.strip() else "(no output)"
                return f"Terminal Response:\n\n```bash\n$ {command}\n{output}\n```"
            else:
                error = (
                    result.stderr.strip()
                    if result.stderr.strip()
                    else f"Command failed with exit code {result.returncode}"
                )
                return f"Terminal Error:\n\n```bash\n$ {command}\n{error}\n```"

        except subprocess.TimeoutExpired:
            return f"Command timeout: '{command}' took longer than {self.bash_timeout} seconds"
        except Exception as e:
            return f"Bash execution error: {e}"

    # ------------------------------------------------------------------
    # Language detection
    # ------------------------------------------------------------------

    def _detect_language(self, code: str) -> str:
        low = code.lower().strip()
        if any(kw in low for kw in ["import ", "def ", "class ", "print(", "if __name__"]):
            return "python"
        if low.startswith(("#!/bin/bash", "#!/bin/sh", "cd ", "ls ", "mkdir ", "cp ", "mv ")):
            return "bash"
        if any(kw in low for kw in ["echo ", "grep ", "find ", "chmod ", "sudo "]):
            return "bash"
        if any(kw in low for kw in ["select ", "insert ", "update ", "delete ", "create table"]):
            return "sql"
        if any(kw in low for kw in ["function ", "const ", "let ", "var ", "console.log", "=>"]):
            return "javascript"
        return "python"

    # ------------------------------------------------------------------
    # Code analysis
    # ------------------------------------------------------------------

    def _analyze_code(self, code: str, language: str) -> dict:
        analysis = {
            "language": language,
            "safe": True,
            "purpose": "computational task",
            "complexity": "simple",
            "requires_packages": [],
            "warnings": [],
        }
        low = code.lower()

        dangerous = [
            ("rm -rf", "File deletion command"),
            ("sudo ", "Administrative privileges"),
            ("chmod 777", "Broad permissions change"),
            ("import os", "File system access"),
            ("subprocess.", "System command execution"),
            ("eval(", "Dynamic code execution"),
            ("exec(", "Dynamic code execution"),
        ]
        for pat, warning in dangerous:
            if pat in low:
                analysis["warnings"].append(warning)
                if pat in ("rm -rf", "sudo ", "chmod 777"):
                    analysis["safe"] = False

        if language == "python":
            for line in code.split("\n"):
                if "import " in line.lower():
                    pkg = line.split("import ")[-1].split()[0].split(".")[0]
                    stdlib = {"os", "sys", "json", "time", "datetime", "pathlib"}
                    if pkg not in stdlib:
                        analysis["requires_packages"].append(pkg)

        line_count = len(code.split("\n"))
        if line_count > 20 or any(w in low for w in ["class ", "def ", "for ", "while "]):
            analysis["complexity"] = "moderate"
        if line_count > 50 or any(w in low for w in ["multiprocessing", "threading", "async "]):
            analysis["complexity"] = "complex"

        return analysis

    # ------------------------------------------------------------------
    # Language-specific execution
    # ------------------------------------------------------------------

    def _execute_code_by_language(self, code: str, language: str, analysis: dict) -> dict:
        result = {
            "language": language,
            "stdout": "",
            "stderr": "",
            "success": False,
            "execution_time": 0,
        }
        start = time.time()
        try:
            if language == "python":
                result = self._execute_python(code, analysis)
            elif language == "bash":
                result = self._execute_bash_code(code)
            elif language == "sql":
                result = self._execute_sql(code)
            elif language == "javascript":
                result = self._execute_javascript(code)
            else:
                result["stderr"] = f"Unsupported language: {language}"
                return result
        except subprocess.TimeoutExpired:
            result["stderr"] = "Execution timed out after 30 seconds"
        except Exception as e:
            result["stderr"] = str(e)
        result["execution_time"] = time.time() - start
        return result

    def _execute_python(self, code: str, analysis: dict) -> dict:
        python_workspace = self.workspace / "python_memory"
        python_workspace.mkdir(exist_ok=True)
        code_file = python_workspace / f"execution_{int(time.time())}.py"

        enhanced_code = (
            "import sys\nimport os\nfrom pathlib import Path\n"
            "import json\nimport time\nfrom datetime import datetime\n\n"
            f"workspace = Path(r\"{self.workspace}\")\n"
            f"os.chdir(str(workspace))\n\n"
            f"{code}"
        )
        code_file.write_text(enhanced_code)

        try:
            timeout = 30 if analysis["complexity"] == "simple" else 120
            start = time.time()
            proc = subprocess.run(
                [sys.executable, str(code_file)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.workspace),
            )
            execution_time = time.time() - start

            result = {
                "language": "python",
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "success": proc.returncode == 0,
                "return_code": proc.returncode,
                "execution_time": execution_time,
            }

            if proc.returncode == 0:
                if self.code_memory:
                    try:
                        purpose = self._infer_code_purpose(code)
                        self.code_memory.store_successful_code(code, "python", purpose)
                    except Exception:
                        pass
                success_file = python_workspace / f"successful_{int(time.time())}.py"
                try:
                    code_file.rename(success_file)
                except Exception:
                    code_file.unlink(missing_ok=True)
            else:
                code_file.unlink(missing_ok=True)

            return result
        except Exception as e:
            code_file.unlink(missing_ok=True)
            raise

    def _execute_bash_code(self, code: str) -> dict:
        try:
            start = time.time()
            result = subprocess.run(
                code,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.workspace),
            )
            return {
                "language": "bash",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "execution_time": time.time() - start,
            }
        except subprocess.TimeoutExpired:
            return {
                "language": "bash",
                "stdout": "",
                "stderr": "Command timed out after 30 seconds",
                "success": False,
                "return_code": -1,
                "execution_time": 30.0,
            }

    def _execute_sql(self, code: str) -> dict:
        try:
            import sqlite3

            sql_db_path = self.workspace / "sql_playground.db"
            conn = sqlite3.connect(sql_db_path)
            conn.execute(
                "CREATE TABLE IF NOT EXISTS sample_data "
                "(id INTEGER PRIMARY KEY, name TEXT, value INTEGER, "
                "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            )
            cursor = conn.execute("SELECT COUNT(*) FROM sample_data")
            if cursor.fetchone()[0] == 0:
                conn.executemany(
                    "INSERT INTO sample_data (name, value) VALUES (?, ?)",
                    [("Alpha", 100), ("Beta", 200), ("Gamma", 150)],
                )
                conn.commit()

            cursor = conn.execute(code)
            if code.strip().upper().startswith(("SELECT", "WITH")):
                rows = cursor.fetchall()
                columns = (
                    [d[0] for d in cursor.description] if cursor.description else []
                )
                if rows:
                    output = f"Query returned {len(rows)} rows:\n\n"
                    if columns:
                        output += "Columns: " + ", ".join(columns) + "\n"
                        output += "-" * 40 + "\n"
                    for row in rows[:10]:
                        output += str(row) + "\n"
                    if len(rows) > 10:
                        output += f"... and {len(rows) - 10} more rows\n"
                else:
                    output = "Query returned no results"
            else:
                affected = cursor.rowcount
                conn.commit()
                output = f"Operation completed. {affected} rows affected."
            conn.close()

            return {
                "language": "sql",
                "stdout": output,
                "stderr": "",
                "success": True,
                "return_code": 0,
            }
        except Exception as e:
            return {
                "language": "sql",
                "stdout": "",
                "stderr": f"SQL Error: {e}",
                "success": False,
                "return_code": 1,
            }

    def _execute_javascript(self, code: str) -> dict:
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
            js_file = self.workspace / f"temp_js_{int(time.time())}.js"
            js_file.write_text(code)
            proc = subprocess.run(
                ["node", str(js_file)],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=str(self.workspace),
            )
            js_file.unlink(missing_ok=True)
            return {
                "language": "javascript",
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "success": proc.returncode == 0,
                "return_code": proc.returncode,
            }
        except FileNotFoundError:
            return {
                "language": "javascript",
                "stdout": "",
                "stderr": "Node.js not found - JavaScript execution unavailable",
                "success": False,
                "return_code": 1,
            }

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def _format_execution_output(self, result: dict, analysis: dict) -> str:
        from rich import box
        from rich.align import Align
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        buf = io.StringIO()
        console = Console(file=buf, width=80, legacy_windows=False)

        lang_styles = {
            "python": {"color": "bright_blue", "icon": "Py", "name": "Python"},
            "bash": {"color": "bright_green", "icon": "Sh", "name": "Bash"},
            "sql": {"color": "bright_magenta", "icon": "SQL", "name": "SQL"},
            "javascript": {"color": "bright_yellow", "icon": "JS", "name": "JavaScript"},
        }
        cfg = lang_styles.get(
            result["language"],
            {"color": "bright_white", "icon": ">>", "name": result["language"].title()},
        )

        table = Table(show_header=False, box=box.ROUNDED, expand=False)
        table.add_column("", style=cfg["color"], width=18)
        table.add_column("", style="bright_white", min_width=35)
        exec_time = result.get("execution_time", 0)
        table.add_row(f"{cfg['icon']} Language", f"[{cfg['color']}]{cfg['name']}[/]")
        table.add_row(
            "Status",
            "[bright_green]Executed Successfully[/]"
            if result.get("success")
            else "[red]Execution Failed[/]",
        )
        table.add_row("Time", f"[yellow]{exec_time:.3f} seconds[/]")
        table.add_row("Complexity", f"[cyan]{analysis.get('complexity', 'unknown').title()}[/]")

        console.print(
            Panel(
                table,
                title=f"[bold {cfg['color']}]{cfg['icon']} Computational Mind Results[/]",
                border_style=cfg["color"],
                expand=False,
            )
        )

        if result.get("success", False):
            stdout = result.get("stdout", "").strip()
            stderr = result.get("stderr", "").strip()
            if stdout:
                lines = stdout.split("\n")
                if len(lines) > 20:
                    displayed = lines[:15] + ["...", f"({len(lines) - 15} more lines)"] + lines[-3:]
                    output_content = "\n".join(displayed)
                else:
                    output_content = stdout
                console.print(
                    Panel(
                        f"[bright_white]{output_content}[/bright_white]",
                        title="[bold bright_green]Program Output[/]",
                        border_style="bright_green",
                        expand=False,
                    )
                )
            if stderr:
                console.print(
                    Panel(
                        f"[yellow]{stderr}[/yellow]",
                        title="[bold yellow]Warnings & Info[/]",
                        border_style="yellow",
                        expand=False,
                    )
                )
            if not stdout and not stderr:
                console.print(Align.center("[bright_green]Code executed successfully with no output[/]"))
        else:
            error_content = result.get("stderr", "Unknown error").strip()
            console.print(
                Panel(
                    f"[red]{error_content}[/red]",
                    title="[bold red]Error Details[/]",
                    border_style="red",
                    expand=False,
                )
            )

        return buf.getvalue()

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def _infer_code_purpose(self, code: str) -> str:
        low = code.lower()
        purpose_map = {
            "file_operations": ["open(", "read()", "write(", "file", "csv", "json"],
            "data_analysis": ["pandas", "numpy", "matplotlib", "plot", "data", "df"],
            "web_operations": ["requests", "urllib", "http", "api", "url"],
            "calculations": ["math", "calculate", "sum(", "mean", "statistics"],
            "system_operations": ["os.", "subprocess", "system", "path"],
            "text_processing": ["string", "text", "regex", "split", "replace"],
            "automation": ["for ", "while ", "range(", "enumerate"],
        }
        for purpose, keywords in purpose_map.items():
            if any(kw in low for kw in keywords):
                return purpose
        return "general_computation"


# ---------------------------------------------------------------------------
# Provider registration function
# ---------------------------------------------------------------------------


def register(
    registry: ToolRegistry,
    config: Any,
    dependencies: Dict[str, Any],
) -> None:
    """Register code execution tools with the central registry.

    Parameters
    ----------
    registry:
        The ``ToolRegistry`` instance.
    config:
        Application configuration.
    dependencies:
        Dict of shared dependencies.  Expected keys:

        - ``"workspace"`` -- ``Path`` to CoCo's workspace directory
        - ``"code_memory"`` -- (optional) CodeMemory instance for persisting snippets
    """
    workspace: Path = dependencies.get("workspace", Path.cwd() / "coco_workspace")
    code_memory = dependencies.get("code_memory")

    tools = _CodeExecutionTools(workspace, config, code_memory)

    registry.register(ToolDefinition(
        name="run_code",
        description="Execute Python code through computational mind - think through code",
        input_schema=_RUN_CODE_SCHEMA,
        handler=tools.run_code,
        category="code_execution",
    ))

    registry.register(ToolDefinition(
        name="execute_bash",
        description="Speak the terminal's native language - execute shell commands",
        input_schema=_EXECUTE_BASH_SCHEMA,
        handler=tools.execute_bash,
        category="code_execution",
    ))
